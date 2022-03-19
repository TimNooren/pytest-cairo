%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin


@constructor
func constructor{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
}():
    return ()
end


@storage_var
func some_storage_var() -> (val : felt):
end


@external
func write_to_some_storage_var{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> ():
    some_storage_var.write(9)
    return ()
end
