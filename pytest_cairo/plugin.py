import asyncio
from typing import Any, Iterable, Optional, Union

import py
import pytest
from _pytest._code.code import ExceptionInfo, TerminalRepr
from _pytest.nodes import Collector, Node
from starkware.starknet.testing.starknet import StarknetContract
from starkware.starkware_utils.error_handling import StarkException

from pytest_cairo.context import Context


class CairoItem(pytest.Item):

    def __init__(
        self, name: str,
        parent: Optional[Node],
        context: Context,
        contract: StarknetContract,
        contract_function_name: str,
    ) -> None:
        super().__init__(name, parent)
        self.context = context
        self.contract = contract
        self.contract_function_name = contract_function_name

    def runtest(self) -> None:
        contract_function = getattr(self.contract, self.contract_function_name)
        # `invoke` is faster than `call`.
        asyncio.run(contract_function().invoke())
        self.context.rollback()

    def repr_failure(
        self, excinfo: ExceptionInfo[BaseException], *_: Any,
    ) -> Union[str, TerminalRepr]:
        if isinstance(excinfo.value, StarkException):
            return repr(excinfo.value)
        else:
            return ''


class CairoFile(pytest.File):

    def collect(self) -> Iterable[Union[CairoItem, Collector]]:
        assert isinstance(self.fspath, py.path.local)
        context = Context()
        contract = context.deploy_contract(source=self.fspath.strpath)
        context.set_checkpoint()
        for contract_function_name in contract._abi_function_mapping:
            if not contract_function_name.startswith('test'):
                continue
            yield CairoItem.from_parent(
                self,
                name=contract_function_name,
                context=context,
                contract=contract,
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
