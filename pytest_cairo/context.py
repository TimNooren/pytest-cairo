import asyncio
from typing import List

from starkware.starknet.compiler.compile import compile_starknet_files
from starkware.starknet.testing.starknet import Starknet, StarknetContract
from starkware.starknet.testing.state import StarknetState


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

    def deploy_contract(self, source: str) -> StarknetContract:
        contract_def = compile_starknet_files(
            files=[source],
            debug_info=True,
        )
        constructor_calldata = create_dummy_constructor_calldata(
            contract_def.abi,
        )
        contract = asyncio.run(self.starknet.deploy(
            contract_def=contract_def,
            constructor_calldata=constructor_calldata,
        ))
        self.deployed_contracts.append(contract)
        return contract
