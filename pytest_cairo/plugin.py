from typing import TYPE_CHECKING, Iterable, Optional, Union

import py
import pytest
from _pytest._code.code import ExceptionInfo, TerminalRepr
from _pytest.nodes import Collector, Node

from pytest_cairo.context import Context
from pytest_cairo.contract import TestFunction

if TYPE_CHECKING:
    # Imported here due to circular import.
    from _pytest._code.code import _TracebackStyle


class CairoItem(pytest.Item):

    def __init__(
        self,
        parent: Optional[Node],
        test_function: TestFunction,
    ) -> None:
        super().__init__(test_function.name, parent)
        self.test_function = test_function

    def runtest(self) -> None:
        self.test_function.invoke()

    def repr_failure(
        self,
        excinfo: ExceptionInfo[BaseException],
        style: 'Optional[_TracebackStyle]' = None,
    ) -> Union[str, TerminalRepr]:
        return super().repr_failure(excinfo, style='short')


class CairoFile(pytest.File):

    def collect(self) -> Iterable[Union[CairoItem, Collector]]:
        assert isinstance(self.fspath, py.path.local)
        context = Context()
        test_contract = context.deploy_contract(source=self.fspath.strpath)
        for test_function in test_contract.test_functions:
            yield CairoItem.from_parent(self, test_function=test_function)


def pytest_collect_file(
    path: py.path.local,
    parent: Collector,
) -> Optional[Collector]:
    if path.ext == '.cairo' and path.basename.startswith('test_'):
        return CairoFile.from_parent(parent, fspath=path)
    else:
        return None
