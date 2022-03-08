import asyncio
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
    StarknetPreprocessedProgram,
)
from starkware.starknet.services.api.contract_definition import (
    ContractDefinition,
)
from starkware.starknet.testing.starknet import Starknet, StarknetContract
from starkware.starknet.testing.state import StarknetState

from pytest_cairo.contract import TestContractWrapper
from pytest_cairo.info_collector import ContractFunctionInfoCollector


def create_dummy_constructor_calldata(abi: List[dict]) -> List[int]:

    constructor_def = next(
        filter(lambda x: x['type'] == 'constructor', abi),
        None,
    )
    if constructor_def is None:
        return []
    else:
        return [0 for _ in constructor_def['inputs']]


class Context:

    def __init__(self) -> None:
        self.starknet = asyncio.run(Starknet.empty())
        self._checkpoint = self.starknet.state.copy()

        self.deployed_contracts: List[StarknetContract] = []

    @property
    def checkpoint(self) -> StarknetState:
        return self._checkpoint.copy()

    def set_checkpoint(self) -> None:
        self._checkpoint = self.starknet.state.copy()

    def rollback(self) -> None:
        self.starknet.state = self.checkpoint
        for contract in self.deployed_contracts:
            contract.state = self.starknet.state

    def deploy_contract(self, source: str) -> TestContractWrapper:
        contract_def, info_collector = compile_starknet_contracts([source])
        constructor_calldata = create_dummy_constructor_calldata(
            contract_def.abi,
        )
        contract = asyncio.run(self.starknet.deploy(
            contract_def=contract_def,
            constructor_calldata=constructor_calldata,
        ))
        self.deployed_contracts.append(contract)
        return TestContractWrapper(contract, contract_def, info_collector)


def compile_starknet_contracts(
    files: List[str],
    cairo_path: List[str] = [],
    debug_info: bool = True,
) -> Tuple[ContractDefinition, ContractFunctionInfoCollector]:

    pass_manager = starknet_pass_manager(
        prime=DEFAULT_PRIME,
        read_module=get_module_reader(cairo_path=cairo_path).read,
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
        preprocessed.auxiliary_info,
    )
