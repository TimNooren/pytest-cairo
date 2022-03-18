import asyncio
import contextlib
import re
from dataclasses import dataclass
from typing import Any, Dict, Generator, Iterator, List, Optional

from _pytest.outcomes import fail
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType
from starkware.cairo.lang.compiler.constants import MAIN_SCOPE
from starkware.cairo.lang.compiler.identifier_definition import (
    FunctionDefinition,
)
from starkware.cairo.lang.compiler.preprocessor.preprocessor import (
    AttributeScope,
)
from starkware.starknet.services.api.contract_definition import (
    ContractDefinition,
)
from starkware.starknet.testing.contract import (
    StarknetContractFunctionInvocation,
)
from starkware.starknet.testing.contract_utils import parse_arguments
from starkware.starknet.testing.objects import StarknetTransactionExecutionInfo
from starkware.starknet.testing.starknet import StarknetContract
from starkware.starkware_utils.error_handling import StarkException

from pytest_cairo.info_collector import (
    ContractFunctionInfo, ContractFunctionInfoCollector,
)

FIXTURE_DECORATOR = 'test_fixture'


@dataclass
class ExpectedException:
    start_pc: int
    end_pc: int
    message: Optional[str]

    @classmethod
    def from_attribute_scope(
        cls, attribute_scope: AttributeScope,
    ) -> 'ExpectedException':
        return cls(
            start_pc=attribute_scope.start_pc,
            end_pc=attribute_scope.end_pc,
            message=attribute_scope.value,
        )


@contextlib.contextmanager
def catch_expected_exceptions(
    expected_exceptions: List[ExpectedException],
) -> Iterator[None]:

    if len(expected_exceptions) > 1:
        raise ValueError('Currently one "raises" block allowed per function.')

    expected = next(iter(expected_exceptions), None)

    try:
        yield
    except StarkException as e:
        if not expected:
            raise

        # Get the pc values of the traceback entries and check whether any
        # of them occurred inside the "raises" block. REVIEW: Ideally we
        # would access the actual traceback entries (and not resort to
        # regex), but I haven't found a way to access those.
        pc_pattern = r'pc=\d+:(\d+)'
        if not any(
            expected.start_pc <= int(traceback_pc) < expected.end_pc
            for traceback_pc in re.findall(pc_pattern, e.message)
        ):
            raise

        if re.search(expected.message or '', e.message):
            return
        raise
    else:
        if expected:
            fail(f'Did not raise "{expected}"')


class TestFunction:
    def __init__(
        self,
        info: ContractFunctionInfo,
        function_invocation: StarknetContractFunctionInvocation,
        expected_exceptions: List[ExpectedException],
    ) -> None:
        self._info = info
        self._function_invocation = function_invocation
        self.expected_exceptions = expected_exceptions

    def invoke(self) -> None:
        with catch_expected_exceptions(self.expected_exceptions):
            asyncio.run(self._function_invocation.invoke())

    @property
    def name(self) -> str:
        return self._info.name


class Fixture:

    def __init__(
        self,
        func: StarknetContractFunctionInvocation,
        return_type: Optional[CairoType],
    ) -> None:
        self.func = func
        self.return_type = return_type
        self._result: Optional[Any] = None

    @property
    def result(self) -> Any:
        if self._result is None:
            execution_info: StarknetTransactionExecutionInfo = asyncio.run(
                self.func.invoke(),
            )
            self._result = execution_info.result[0]
        return self._result


class TestContract:

    def __init__(
        self,
        contract: StarknetContract,
        contract_def: ContractDefinition,
        preprocessed: ContractFunctionInfoCollector,
    ) -> None:
        self.contract = contract
        self.contract_def = contract_def
        self.preprocessed = preprocessed
        self.info_collector = preprocessed.auxiliary_info

        self._fixtures: Optional[Dict[str, Fixture]] = None

    @property
    def test_functions(self) -> Generator[TestFunction, None, None]:
        for abi_entry in self.contract_def.abi:
            if abi_entry['type'] != 'function':
                continue

            function_name = abi_entry['name']
            if not function_name.startswith('test'):
                continue

            function_info = self.info_collector.get_function_info(
                MAIN_SCOPE + function_name,
            )
            expected_exceptions = self.get_expected_exceptions_for_function(
                self.contract_def, function_info)

            arg_names, _ = parse_arguments(abi_entry['inputs'])

            args_from_fixtures = {
                arg_name: self.fixtures[arg_name].result
                for arg_name in arg_names
            }

            function_invocation = self.contract.get_contract_function(
                function_name)(**args_from_fixtures)

            # Copy contract state so each function runs in isolation.
            function_invocation.state = self.contract.state.copy()

            yield TestFunction(
                info=function_info,
                function_invocation=function_invocation,
                expected_exceptions=expected_exceptions,
            )

    @property
    def fixtures(self) -> Dict[str, Fixture]:
        if self._fixtures is None:

            self._fixtures = {}
            identifiers = self.preprocessed.identifiers

            for abi_entry in self.contract_def.abi:
                if abi_entry['type'] != 'function':
                    continue

                function_name = abi_entry['name']

                definition = identifiers.dict[MAIN_SCOPE + function_name]
                if not isinstance(definition, FunctionDefinition):
                    continue
                if FIXTURE_DECORATOR not in definition.decorators:
                    continue

                func = self.contract.get_contract_function(function_name)()

                _, return_types = parse_arguments(abi_entry['outputs'])
                if len(return_types) == 0:
                    return_type = None
                elif len(return_types) == 1:
                    return_type = return_types[0]
                else:
                    raise Exception(
                        f'Fixture {function_name} returns more than 1 value.')

                self._fixtures[function_name] = Fixture(func, return_type)
        return self._fixtures

    @staticmethod
    def get_expected_exceptions_for_function(
        contract_def: ContractDefinition,
        function_info: ContractFunctionInfo,
    ) -> List[ExpectedException]:
        return [
            ExpectedException.from_attribute_scope(attr)
            for attr in contract_def.program.attributes
            if attr.name == 'raises' and
            # Check if attribute is inside the function
            function_info.start_pc <= attr.start_pc < function_info.end_pc
        ]
