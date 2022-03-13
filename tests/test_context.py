from typing import List

import pytest

from pytest_cairo.context import Context


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
    context = Context()
    expected = constructor_calldata
    actual = context.create_dummy_constructor_calldata(abi)
    assert actual == expected
