from _pytest.pytester import Pytester

from tests import RESOURCES_DIR


def test_plugin(pytester: Pytester) -> None:
    # Note: `copy_example` requires pytester_example_dir to be set in the
    # pytest config.
    pytester.copy_example(str(RESOURCES_DIR))
    run_result = pytester.runpytest()
    run_result.assert_outcomes(passed=3)
