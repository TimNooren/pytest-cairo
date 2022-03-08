import asyncio
from typing import TYPE_CHECKING, Iterable, Optional, Union

import py
import pytest
from _pytest._code.code import ExceptionInfo, TerminalRepr
from _pytest.nodes import Collector, Node

from pytest_cairo.context import Context
from pytest_cairo.contract import TestContractWrapper, TestFunction

if TYPE_CHECKING:
    # Imported here due to circular import.
    from _pytest._code.code import _TracebackStyle


class CairoItem(pytest.Item):

    def __init__(
        self,
        name: str,
        parent: Optional[Node],
        context: Context,
        contract_wrapper: TestContractWrapper,
        contract_function_name: str,
    ) -> None:
        super().__init__(name, parent)
        self.context = context
        self.contract_wrapper = contract_wrapper
        self.contract_function_name = contract_function_name

    def runtest(self) -> None:
        with TestFunction(
            self.contract_wrapper, self.contract_function_name,
        ) as func:
            asyncio.run(func.invoke())

        self.context.rollback()

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
        contract_wrapper = context.deploy_contract(
            source=self.fspath.strpath)
        context.set_checkpoint()
        for abi_entry in contract_wrapper.contract_def.abi:
            contract_function_name = abi_entry['name']
            if not contract_function_name.startswith('test'):
                continue
            yield CairoItem.from_parent(
                self,
                name=contract_function_name,
                context=context,
                contract_wrapper=contract_wrapper,
                contract_function_name=contract_function_name,
            )


def pytest_collect_file(
    path: py.path.local,
    parent: Collector,
) -> Optional[Collector]:
    if path.ext == '.cairo' and path.basename.startswith('test_'):
        return CairoFile.from_parent(parent, fspath=path)
    else:
        return None
