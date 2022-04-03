from _pytest.pytester import Pytester

from tests import RESOURCES_DIR


def test_plugin(pytester: Pytester) -> None:
    pytester.makepyprojecttoml("""
[tool.pytest.ini_options]
disable_contract_hash_computation=true
""")

    # Note: `copy_example` requires pytester_example_dir to be set in the
    # pytest config.
    pytester.copy_example(str(RESOURCES_DIR))
    run_result = pytester.runpytest_inprocess()
    run_result.assert_outcomes(passed=12)
