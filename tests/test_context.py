from typing import List

import pytest

from pytest_cairo.context import Context, create_dummy_constructor_calldata


@pytest.mark.parametrize('abi,constructor_calldata', [
    ([], []),
    ([{'type': 'constructor', 'inputs': []}], []),
    (
        [{'type': 'constructor', 'inputs': [{'name': 'foo', 'type': 'bar'}]}],
        [0],
    ),
])
def test_create_dummy_constructor_calldata(
    abi: List[dict],
    constructor_calldata: List[int],
) -> None:
    expected = constructor_calldata
    actual = create_dummy_constructor_calldata(abi)
    assert actual == expected


def test_set_checkpoint() -> None:
    context = Context()

    # Checkpoint starts out empty:
    assert context._checkpoint.state.contract_states == {}

    context.starknet.state.state.contract_states['foo'] = 'bar'
    context.set_checkpoint()

    # Checkpoint has been updated:
    assert context._checkpoint.state.contract_states == {'foo': 'bar'}

    context.starknet.state.state.contract_states['fizz'] = 'buzz'

    # Checkpoint state has not been affected by second contract state update:
    assert context._checkpoint.state.contract_states == {'foo': 'bar'}


def test_rollback() -> None:
    context = Context()

    # Checkpoint starts out empty:
    assert context._checkpoint.state.contract_states == {}

    context.starknet.state.state.contract_states['foo'] = 'bar'

    # Checkpoint state has not been affected by contract state update:
    assert context._checkpoint.state.contract_states == {}

    context.rollback()

    # Checkpoint has not been affected by rollback:
    assert context._checkpoint.state.contract_states == {}
    # Context state matches checkpoint after rollback:
    assert context.starknet.state.state == context._checkpoint.state

    context.starknet.state.state.contract_states['fizz'] = 'buzz'
    # Checkpoint has not been affected by second contract state update:
    assert context._checkpoint.state.contract_states == {}
