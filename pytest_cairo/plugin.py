import shutil
import tempfile
from pathlib import Path
from typing import Iterable, Optional, Union

import py
import pytest
from pytest import Collector, Config, Parser, PytestPluginManager, StashKey

import pytest_cairo
from pytest_cairo.context import Context
from pytest_cairo.contract_index import generate_contract_index
from pytest_cairo.patch import disable_contract_hash_computation

PYTEST_CAIRO_TEMP_DIR_KEY = StashKey[str]()


def pytest_addoption(
    parser: Parser, pluginmanager: PytestPluginManager,
) -> None:
    help = 'Disable computation of contract hash to speed up tests.'
    name = 'disable_contract_hash_computation'
    default = False
    parser.addoption(
        '--disable-contract-hash-computation',
        action='store_true',
        dest=name,
        default=default,
        help='Disable computation of contract hash to speed up tests.',
    )
    parser.addini(name=name, type='bool', default=default, help=help)


def pytest_configure(config: Config) -> None:
    if (
        config.getoption('disable_contract_hash_computation') or
        config.getini('disable_contract_hash_computation')
    ):
        disable_contract_hash_computation()

    temp_dir = tempfile.TemporaryDirectory()
    config.add_cleanup(temp_dir.cleanup)
    config.stash[PYTEST_CAIRO_TEMP_DIR_KEY] = temp_dir.name

    target_dir = Path(temp_dir.name) / 'pytest_cairo'
    target_dir.mkdir(parents=True, exist_ok=True)

    with (target_dir / 'contract_index.cairo').open('w') as f:
        f.write(generate_contract_index(root=Path.cwd()))

    shutil.copy(
        Path(pytest_cairo.__file__).parent / 'helpers.cairo',
        target_dir,
    )


class CairoItem(pytest.Function):
    ...


class CairoFile(pytest.Module):

    def collect(self) -> Iterable[Union[CairoItem, Collector]]:
        assert isinstance(self.path, Path)
        context = Context(cairo_path=[
            self.config.stash[PYTEST_CAIRO_TEMP_DIR_KEY],
        ])
        test_contract = context.deploy_contract(source=str(self.path))

        self.session._fixturemanager.parsefactories(
            test_contract.fixtures, nodeid=self.nodeid,
        )

        for test_function in test_contract.test_functions:
            yield CairoItem.from_parent(
                self, name=test_function.__name__, callobj=test_function,
            )


def pytest_collect_file(
    path: py.path.local,
    parent: Collector,
) -> Optional[Collector]:
    if path.ext == '.cairo' and path.basename.startswith('test_'):
        return CairoFile.from_parent(parent, path=Path(path))
    else:
        return None
