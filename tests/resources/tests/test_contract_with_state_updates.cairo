# Test if state is rolled back correctly between test function invocations.
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

from contracts.contract_with_state_updates import some_storage_var, write_to_some_storage_var


func _test_write_to_some_storage_var{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> ():

    let (result) = some_storage_var.read()
    assert result = (0)

    write_to_some_storage_var()

    let (result) = some_storage_var.read()
    assert result = (9)

    return()
end


@external
func test_first_call{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> ():

    _test_write_to_some_storage_var()

    return()
end


@external
func test_second_call{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> ():

    _test_write_to_some_storage_var()

    return()
end
