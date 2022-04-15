from types import ModuleType
from typing import Generator, List, Optional

import pytest
from starkware.cairo.lang.compiler.constants import MAIN_SCOPE
from starkware.cairo.lang.compiler.identifier_definition import (
    FunctionDefinition,
)
from starkware.starknet.services.api.contract_definition import (
    ContractDefinition,
)
from starkware.starknet.testing.starknet import StarknetContract

from pytest_cairo.fixture import FIXTURE_DECORATOR, FixtureFunction
from pytest_cairo.function import ExpectedException, TestFunction
from pytest_cairo.info_collector import (
    ContractFunctionInfo, ContractFunctionInfoCollector,
)


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

        # ModuleType since that is what pytest understands when collecting
        # fixtures, and we want to leverage existing functionality as much
        # as possible.
        self._fixtures: Optional[ModuleType] = None

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

            func = self.contract.get_contract_function(function_name)

            yield TestFunction(
                func=func,
                abi=abi_entry,
                expected_exceptions=expected_exceptions,
            )

    @property
    def fixtures(self) -> ModuleType:
        if self._fixtures is None:

            self._fixtures = ModuleType(f'fixtures_{id(self)}')
            identifiers = self.preprocessed.identifiers

            for abi_entry in self.contract_def.abi:
                if abi_entry['type'] != 'function':
                    continue

                function_name = abi_entry['name']

                definition = identifiers.dict.get(MAIN_SCOPE + function_name)
                if definition is None:
                    continue
                if not isinstance(definition, FunctionDefinition):
                    continue
                if FIXTURE_DECORATOR not in definition.decorators:
                    continue

                func = self.contract.get_contract_function(function_name)

                setattr(self._fixtures, function_name, pytest.fixture(
                    FixtureFunction(func, abi_entry), scope='module',
                ))

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
