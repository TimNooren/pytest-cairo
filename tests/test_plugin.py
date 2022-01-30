import sys

import pytest
from _pytest.pytester import Pytester

pytestmark = pytest.mark.xfail(
    sys.version_info >= (3, 10),
    reason='Issue in cairo-lang. '
    'See https://github.com/starkware-libs/cairo-lang/issues/27',
)


def test_plugin(pytester: Pytester) -> None:
    # Note: `copy_example` requires pytester_example_dir to be set in the
    # pytest config.
    pytester.copy_example('tests/resources/')
    run_result = pytester.runpytest()
    run_result.assert_outcomes(passed=1)
