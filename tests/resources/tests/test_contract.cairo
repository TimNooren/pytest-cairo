# We must use the 'starknet' directive here because we are importing from a
# module that uses it.
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

from contracts.contract import calculate_inverse


# Function must be marked as 'external' to allow the plugin to call it.
@external
func test_calculate_inverse{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> ():
    let (actual) = calculate_inverse(2)
    let expected = 1 / 2
    assert actual = expected
    return ()
end


@external
func test_calculate_inverse_expected_exception{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> ():
    with_attr raises("assert_not_zero failed"):
        calculate_inverse(0)
    end
    return ()
end
