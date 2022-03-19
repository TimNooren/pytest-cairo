pytest-cairo: pytest support for cairo-lang and starknet
---

## Usage
To install:
```bash
$ pip install pytest-cairo
```
The plugin will automatically run any function with a `test` prefix, from files with a `test_` prefix and a `.cairo` extension.

## Examples

### Basic tests

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

### Deploying contracts

Contracts can be deployed from tests using the `deploy_contract` helper function. Consider the same contract from the previous example, but extended with a constructor:
```
# Contents of contracts/contract.cairo
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@constructor
func constructor{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
}(arg : felt):
    return ()
end

func calculate_inverse{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}(val : felt) -> (res : felt):
    return (1 / val)
end
```
We can deploy this contract in our `test_contract` function and call its methods:
```
%lang starknet

from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.cairo_builtins import HashBuiltin

from contracts.interfaces.IContract import IContract

from pytest_cairo.contract_index import contracts
from pytest_cairo.helpers import deploy_contract

@view
func test_contract{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr,
}() -> ():

    let (calldata : felt*) = alloc()
    assert calldata[0] = 1  # Value is not relevant
    let (contract_address) = deploy_contract(contracts.contract, 1, calldata)

    let (result) = IContract.calculate_inverse(
        contract_address=contract_address, val=4)

    assert result = 1/4

    return ()
end
```
The `contract_index` provides a reference to contracts and is generated automatically by indexing folders that contain `.cairo` files in the current working directory. In the above example the contract `contract.cairo` is located in a folder called `contracts`, so we can reference it as `contracts.contract`.

### Other helper functions

Other available helper functions:
- `set_block_number`: sets the current block number
- `set_block_timestamp`: sets the current block timestamp
- `set_caller_address`: sets the caller address returned by `get_caller_address`
- `set_contract_address`: sets the contract address of the current test contract. This is useful when calling other contracts, since this address will be returned when the other contract calls `get_caller_address`
- `impersonate`: sets both the caller address and the contract address. The former is useful when testing functions directly, the latter when calling functions in other contracts

Helper functions can be imported from `pytest_cairo.helpers`.

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
