from typing import List

import pytest
from _pytest.pytester import Pytester

from pytest_cairo.plugin import create_dummy_constructor_calldata


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


def test_plugin(pytester: Pytester) -> None:
    # Note: `copy_example` requires pytester_example_dir to be set in the
    # pytest config.
    pytester.copy_example('tests/resources/')
    run_result = pytester.runpytest()
    run_result.assert_outcomes(passed=1)
