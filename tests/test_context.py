from pytest_cairo.context import Context


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
