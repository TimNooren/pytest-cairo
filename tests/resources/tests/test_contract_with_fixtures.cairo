%lang starknet

from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.cairo_builtins import HashBuiltin

from contracts.contract import calculate_inverse


struct Param:
    member val : felt
    member expected : felt
end


@view
@test_fixture
func param() -> (res : Param):
    return (Param(val=2, expected=1/2))
end


@view
func test_calculate_inverse{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}(param : Param) -> ():
    let (actual) = calculate_inverse(param.val)
    assert actual = param.expected
    return ()
end
