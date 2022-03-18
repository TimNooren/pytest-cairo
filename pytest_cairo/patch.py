from typing import Callable

from starkware.starknet.core.os import contract_hash
from starkware.starknet.services.api.contract_definition import (
    ContractDefinition,
)


def disable_contract_hash_computation() -> None:
    def patch(
        contract_definition: ContractDefinition,
        hash_func: Callable[[int, int], int],
    ) -> int:
        return id(contract_definition)

    contract_hash.compute_contract_hash_inner = patch
