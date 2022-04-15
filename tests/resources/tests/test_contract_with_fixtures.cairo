%lang starknet

from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.cairo_builtins import HashBuiltin

from pytest_cairo.contract_index import contracts
from pytest_cairo.helpers import deploy_contract

from contracts.contract import calculate_inverse
from contracts.interfaces.IContract import IContract


struct Param:
    member val : felt
    member expected : felt
end


@external
@fixture
func deployed() -> (contract_address : felt):
    # Fixture that deploys a contract and returns its contract address.
    let (calldata : felt*) = alloc()
    assert calldata[0] = 12
    assert calldata[1] = 34
    let (contract_address) = deploy_contract(contracts.contract, 2, calldata)
    return (contract_address)
end


@view
@fixture
func _expected() -> (expected : felt):
    # Simple fixture that returns a value but does not rely on any other
    # fixtures.
    return (1/2)
end


@view
@fixture
func _dummy() -> ():
    # Fixture that does not return a value.
    return ()
end


@view
@fixture
func param(_expected : felt) -> (res : Param):
    # Fixture that returns a Struct, and relies on another fixture.
    return (Param(val=2, expected=_expected))
end


@view
func test_calculate_inverse_direct{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}(param : Param, deployed : felt) -> ():
    let (actual) = calculate_inverse(param.val)
    assert actual = param.expected

    return ()
end


@view
func test_calculate_inverse_remote{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}(param : Param, deployed : felt, _dummy : felt) -> ():
    # Test that relies on multiple fixtures.
    # Note that although the _dummy fixture does not return a value, we still
    # need to provide a type for the argument. The plugin will pass a value of
    # 0 in these cases.
    let (actual) = IContract.calculate_inverse(deployed, param.val)
    assert actual = param.expected

    return ()
end
