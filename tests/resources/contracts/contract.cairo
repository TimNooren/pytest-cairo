%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.math import assert_not_zero
from starkware.starknet.common.syscalls import get_caller_address


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


@view
func only_owner{
    syscall_ptr : felt*,
    range_check_ptr,
}() -> ():
    let owner = 123
    let (caller_address) = get_caller_address()
    assert caller_address = owner

    return ()
end
