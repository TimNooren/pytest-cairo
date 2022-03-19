%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.math import assert_not_zero

@constructor
func constructor{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
}(arg1 : felt, arg2 : felt):
    return ()
end

@view
func calculate_inverse{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}(val : felt) -> (res : felt):
    assert_not_zero(val)
    return (1 / val)
end
