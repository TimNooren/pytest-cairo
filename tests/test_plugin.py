from _pytest.pytester import Pytester


def test_plugin(pytester: Pytester) -> None:
    # Note: `copy_example` requires pytester_example_dir to be set in the
    # pytest config.
    pytester.copy_example('tests/resources/')
    run_result = pytester.runpytest()
    run_result.assert_outcomes(passed=1)
