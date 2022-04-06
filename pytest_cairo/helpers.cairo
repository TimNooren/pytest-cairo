
func set_caller_address(address : felt) -> ():
    %{ syscall_handler.caller_address = ids.address %}
    return ()
end


func set_contract_address(address : felt) -> ():
    %{ syscall_handler.contract_address = ids.address %}
    return ()
end


func impersonate(address : felt) -> ():
    %{
        syscall_handler.caller_address = ids.address
        syscall_handler.contract_address = ids.address
    %}
    return ()
end


func set_block_number(block_number : felt) -> ():
    %{ 
        from starkware.starknet.business_logic.state.state import BlockInfo

        current_block_info = syscall_handler.state.block_info
        syscall_handler.state.block_info = BlockInfo(
            ids.block_number,
            current_block_info.block_timestamp,
            current_block_info.gas_price,
        )
    %}
    return ()
end


func set_block_timestamp(block_timestamp : felt) -> ():
    %{ 
        from starkware.starknet.business_logic.state.state import BlockInfo

        current_block_info = syscall_handler.state.block_info
        syscall_handler.state.block_info = BlockInfo(
            current_block_info.block_number,
            ids.block_timestamp,
            current_block_info.gas_price,
        )
    %}
    return ()
end


func deploy_contract(contract_id : felt, calldata_len: felt, calldata: felt*) -> (contract_address : felt):
    alloc_locals

    local contract_address

    %{ 
        import asyncio
        from pathlib import Path
        from typing import Optional

        from starkware.cairo.lang.compiler.identifier_definition import (
            ConstDefinition,
        )
        from starkware.cairo.lang.compiler.preprocessor import local_variables
        from starkware.cairo.lang.compiler.scoped_name import ScopedName
        from starkware.starknet.testing.starknet import Starknet
        from starkware.starknet.testing.state import StarknetState

        starknet_state = StarknetState(
            state=syscall_handler.state,
            general_config=syscall_handler.general_config,
        )
        starknet = Starknet(starknet_state)

        path: Optional[Path] = None

        for scope, definition in ids._context.identifiers.as_dict().items():
            index_scope =ScopedName(('pytest_cairo', 'contract_index'))
            if not scope.startswith(index_scope):
                continue
            if scope.path[-1] == local_variables.N_LOCALS_CONSTANT:
                continue
            if not isinstance(definition, ConstDefinition):
                continue
            if not definition.value == ids.contract_id:
                continue
            path = Path(*scope.path[2:]).with_suffix('.cairo')
            break
        else:
            raise Exception('Could not find contract to deploy.')

        assert path is not None
        
        calldata = [memory[ids.calldata + i] for i in range(ids.calldata_len)]
        contract = asyncio.run(
            starknet.deploy(str(path), constructor_calldata=calldata),
        )
        ids.contract_address = contract.contract_address
    %}
    return (contract_address=contract_address)
end
