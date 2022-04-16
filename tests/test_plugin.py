from pytest import Pytester

from tests import RESOURCES_DIR


def test_plugin(pytester: Pytester) -> None:
    pytester.makepyprojecttoml("""
[tool.pytest.ini_options]
disable_contract_hash_computation=true
""")

    # REVIEW: Not sure if this is a great idea, but it avoids having to
    # `pip install .` to test the plugin.
    pytester.makeconftest("""
pytest_plugins = ("pytest_cairo.plugin",)
""")

    # Note: `copy_example` requires pytester_example_dir to be set in the
    # pytest config.
    pytester.copy_example(str(RESOURCES_DIR))
    run_result = pytester.runpytest_inprocess()
    run_result.assert_outcomes(passed=14)
