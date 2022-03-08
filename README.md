pytest-cairo: pytest support for cairo-lang and starknet
---

## Usage
To install:
```bash
$ pip install pytest-cairo
```
The plugin will automatically run any function with a `test` prefix, from files with a `test_` prefix and a `.cairo` extension.

## Example

Consider the following Starknet contract:
```
# Contents of contract.cairo
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

func calculate_inverse{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}(val : felt) -> (res : felt):
    return (1 / val)
end
```

We could write a basic test for the function `calculate_inverse`:
```
# Contents of test_contract.cairo
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

from contracts.contract import calculate_inverse

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
```
Additionally we could use a `raises` attribute to assert that the function fails if we pass `val=0`:
```
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
```

## Development
To install development dependencies, run:
```bash
$ pip install -r requirements-dev.txt
```
Run tests with:
```bash
$ pytest
```
or:
```bash
$ docker-compose run test
```
To run tests against all supported interpreters (using `docker-compose`):
```bash
$ tox
```
This assumes `tox`, `docker` and `docker-compose` are installed.
