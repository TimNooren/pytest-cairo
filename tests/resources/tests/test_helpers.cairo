%lang starknet

from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address,
    get_contract_address,
)

from contracts.interfaces.IContract import IContract
from pytest_cairo.contract_index import contracts
from pytest_cairo.helpers import (
    deploy_contract, impersonate, set_block_number, set_block_timestamp,
    set_caller_address, set_contract_address,
)


@view
func test_set_caller_address{
    syscall_ptr : felt*,
}() -> ():

    # We are starting out with the standard caller address:
    let (caller_address) = get_caller_address()
    assert caller_address = 0

    # We can override the caller address:
    set_caller_address(123)
    let (caller_address) = get_caller_address()
    assert caller_address = 123
    
    # We can override the caller address again:
    set_caller_address(456)
    let (caller_address) = get_caller_address()
    assert caller_address = 456
    
    return ()
end


@view
func test_set_caller_address_function_isolation{
    syscall_ptr : felt*,
}() -> ():

    # Caller address is not affected by changes in previous tests:
    let (caller_address) = get_caller_address()
    assert caller_address = 0
    return ()
end


@view
func test_set_contract_address{
    syscall_ptr : felt*,
}() -> ():

    let (initial_contract_address) = get_contract_address()

    assert_not_equal(initial_contract_address, 123)
    set_contract_address(123)
    let (contract_address) = get_contract_address()
    assert contract_address = 123

    return ()
end


@view
func test_impersonate{
    syscall_ptr : felt*,
}() -> ():

    let (initial_caller_address) = get_caller_address()
    let (initial_contract_address) = get_contract_address()

    assert initial_caller_address = 0
    assert_not_equal(initial_contract_address, 123)

    impersonate(123)

    let (caller_address) = get_caller_address()
    assert caller_address = 123
    let (contract_address) = get_contract_address()
    assert contract_address = 123

    return ()
end


@view
func test_set_block_number{
    syscall_ptr : felt*,
}() -> ():

    let (block_number) = get_block_number()
    assert block_number = -1

    set_block_number(99)

    let (block_number) = get_block_number()
    assert block_number = 99

    return ()
end


@view
func test_set_block_timestamp{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> ():

    let (block_timestamp) = get_block_timestamp()
    assert block_timestamp = 0

    set_block_timestamp(99)

    let (block_timestamp) = get_block_timestamp()
    assert block_timestamp = 99

    return ()
end


@view
func test_deploy_contract{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> ():

    let (calldata : felt*) = alloc()
    assert calldata[0] = 12
    assert calldata[1] = 34
    let (contract_address) = deploy_contract(contracts.contract, 2, calldata)

    let (result) = IContract.calculate_inverse(
        contract_address=contract_address, val=4)

    assert result = 1/4

    return ()
end
