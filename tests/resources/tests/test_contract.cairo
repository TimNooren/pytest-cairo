# We must use the 'starknet' directive here because we are importing from a
# module that uses it.
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

from contracts.contract import do_the_thing


# Function must be marked as 'external' to allow the plugin to call it.
@external
func test_do_the_thing{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> ():
    let (result) = do_the_thing()
    assert result = (1)
    return()
end
