# We must use the 'starknet' directive here because we are importing from a
# module that uses it.
%lang starknet

# We currently cannot import 'HashBuiltin' independently, so import it from
# the implementation contract.
from contract import HashBuiltin, do_the_thing


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
