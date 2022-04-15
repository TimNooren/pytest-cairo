
import asyncio
import contextlib
import inspect
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Iterator, List, Optional

from pytest import fail
from starkware.cairo.lang.compiler.preprocessor.preprocessor import (
    AttributeScope,
)
from starkware.starknet.testing.objects import StarknetTransactionExecutionInfo
from starkware.starkware_utils.error_handling import StarkException


@dataclass
class ExpectedException:
    start_pc: int
    end_pc: int
    message: Optional[str]

    @classmethod
    def from_attribute_scope(
        cls, attribute_scope: AttributeScope,
    ) -> 'ExpectedException':
        return cls(
            start_pc=attribute_scope.start_pc,
            end_pc=attribute_scope.end_pc,
            message=attribute_scope.value,
        )


@contextlib.contextmanager
def catch_expected_exceptions(
    expected_exceptions: List[ExpectedException],
) -> Iterator[None]:

    if len(expected_exceptions) > 1:
        raise ValueError('Currently one "raises" block allowed per function.')

    expected = next(iter(expected_exceptions), None)

    try:
        yield
    except StarkException as e:
        if not expected:
            raise

        # Get the pc values of the traceback entries and check whether any
        # of them occurred inside the "raises" block. REVIEW: Ideally we
        # would access the actual traceback entries (and not resort to
        # regex), but I haven't found a way to access those.
        pc_pattern = r'pc=\d+:(\d+)'
        if not any(
            expected.start_pc <= int(traceback_pc) < expected.end_pc
            for traceback_pc in re.findall(pc_pattern, e.message)
        ):
            raise

        if re.search(expected.message or '', e.message):
            return
        raise
    else:
        if expected:
            fail(f'Did not raise "{expected}"')


class ContractFunctionBase(ABC):
    def __init__(self, func: Callable, abi: dict) -> None:
        self.func = func
        self.abi = abi

        self.__name__ = abi['name']
        self.__signature__ = inspect.signature(func)

    def call(
        self, *args: Any, **kwargs: Any,
    ) -> StarknetTransactionExecutionInfo:
        return asyncio.run(
            self.func(*args, **kwargs).call(),
        )

    def invoke(
        self, *args: Any, **kwargs: Any,
    ) -> StarknetTransactionExecutionInfo:
        return asyncio.run(
            self.func(*args, **kwargs).invoke(),
        )

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


class TestFunction(ContractFunctionBase):
    def __init__(
        self,
        func: Callable,
        abi: dict,
        expected_exceptions: List[ExpectedException],
    ) -> None:
        super().__init__(func, abi)
        self.expected_exceptions = expected_exceptions

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        with catch_expected_exceptions(self.expected_exceptions):
            self.call(*args, **kwargs)
