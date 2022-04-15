import asyncio
from pathlib import Path
from typing import List, Tuple

from starkware.cairo.lang.cairo_constants import DEFAULT_PRIME
from starkware.cairo.lang.compiler.cairo_compile import (
    compile_cairo_ex, get_codes, get_module_reader,
)
from starkware.cairo.lang.compiler.program import Program
from starkware.starknet.compiler.compile import get_entry_points_by_type
from starkware.starknet.compiler.starknet_pass_manager import (
    starknet_pass_manager,
)
from starkware.starknet.compiler.starknet_preprocessor import (
    SUPPORTED_DECORATORS, StarknetPreprocessedProgram,
)
from starkware.starknet.services.api.contract_definition import (
    ContractDefinition, EntryPointType,
)
from starkware.starknet.testing.starknet import Starknet

from pytest_cairo.contract import TestContract
from pytest_cairo.fixture import FIXTURE_DECORATOR
from pytest_cairo.info_collector import ContractFunctionInfoCollector

SUPPORTED_DECORATORS.add(FIXTURE_DECORATOR)


class Context:

    def __init__(self, cairo_path: List[str] = []) -> None:
        self.cairo_path = cairo_path

        self.starknet = asyncio.run(Starknet.empty())

    def deploy_contract(self, source: str) -> TestContract:
        assert Path(source).is_file()
        contract_def, preprocessed = self.compile_contracts(
            files=[source],
            cairo_path=self.cairo_path,
        )

        contract_def.entry_points_by_type[EntryPointType.CONSTRUCTOR] = []

        contract = asyncio.run(self.starknet.deploy(
            contract_def=contract_def,
        ))
        return TestContract(contract, contract_def, preprocessed)

    @staticmethod
    def compile_contracts(
        files: List[str],
        cairo_path: List[str] = [],
        debug_info: bool = True,
    ) -> Tuple[ContractDefinition, StarknetPreprocessedProgram]:

        pass_manager = starknet_pass_manager(
            prime=DEFAULT_PRIME,
            read_module=get_module_reader(cairo_path=cairo_path).read,
            disable_hint_validation=True,
        )
        for name, stage in pass_manager.stages:
            if name == 'preprocessor':
                stage.auxiliary_info_cls = ContractFunctionInfoCollector

        program, preprocessed = compile_cairo_ex(
            code=get_codes(files),
            debug_info=debug_info,
            pass_manager=pass_manager,
        )

        program = Program.load(data=program.dump())

        assert isinstance(preprocessed, StarknetPreprocessedProgram)
        return (
            ContractDefinition(
                program=program,
                entry_points_by_type=get_entry_points_by_type(program=program),
                abi=preprocessed.abi,
            ),
            preprocessed,
        )
