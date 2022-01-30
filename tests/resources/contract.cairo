%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@view
func do_the_thing{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> (val : felt):
    return (1)
end
