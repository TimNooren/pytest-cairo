import re
from dataclasses import dataclass
from types import TracebackType
from typing import Optional, Type

from _pytest.outcomes import fail
from starkware.cairo.lang.compiler.constants import MAIN_SCOPE
from starkware.cairo.lang.compiler.preprocessor.preprocessor import (
    AttributeScope,
)
from starkware.starknet.services.api.contract_definition import (
    ContractDefinition,
)
from starkware.starknet.testing.contract import (
    StarknetContractFunctionInvocation,
)
from starkware.starknet.testing.starknet import StarknetContract
from starkware.starkware_utils.error_handling import StarkException

from pytest_cairo.info_collector import (
    ContractFunctionInfo, ContractFunctionInfoCollector,
)


@dataclass
class TestContractWrapper:
    starknet_contract: StarknetContract
    contract_def: ContractDefinition
    info_collector: ContractFunctionInfoCollector


class TestFunction:
    def __init__(
        self,
        contract_wrapper: TestContractWrapper,
        contract_function_name: str,
    ) -> None:
        self.contract_wrapper = contract_wrapper
        self.contract_function_name = contract_function_name

    def __enter__(self) -> StarknetContractFunctionInvocation:
        starknet_contract = self.contract_wrapper.starknet_contract
        func_object = starknet_contract.get_contract_function(
            self.contract_function_name,
        )
        return func_object()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        if exc_val is not None:
            if not isinstance(exc_val, StarkException):
                return False

            if not self._expected_exception:
                return False

            # Get the pc values of the traceback entries and check whether any
            # of them occurred inside the "raises" block. REVIEW: Ideally we
            # would access the actual traceback entries (and not resort to
            # regex), but I haven't found a way to access those.
            pc_pattern = r'pc=\d+:(\d+)'
            block_start_pc = self._expected_exception.start_pc
            block_end_pc = self._expected_exception.end_pc
            if not any(
                block_start_pc <= int(traceback_pc) < block_end_pc
                for traceback_pc in re.findall(pc_pattern, exc_val.message)
            ):
                return False

            if re.search(
                self._expected_exception.value or '',
                exc_val.message,
            ):
                return True
        else:
            if self._expected_exception:
                fail(f'Did not raise "{self._expected_exception.value}"')

        return False

    @property
    def _expected_exception(self) -> Optional[AttributeScope]:
        attrs = [
            attr
            for attr in self.contract_wrapper.contract_def.program.attributes
            if attr.name == 'raises' and (
                # Check if attribute is inside the current function
                attr.start_pc >= self._contract_function_info.start_pc and
                attr.start_pc < self._contract_function_info.end_pc
            )
        ]
        assert len(attrs) <= 1, 'One "raises" block allowed per function.'

        if attrs:
            return attrs[0]
        else:
            return None

    @property
    def _contract_function_info(self) -> ContractFunctionInfo:
        return self.contract_wrapper.info_collector.get_function_info(
            MAIN_SCOPE + self.contract_function_name,
        )
