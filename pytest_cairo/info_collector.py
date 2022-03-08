from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from starkware.cairo.lang.compiler.ast.expr import ExprAssignment, Expression
from starkware.cairo.lang.compiler.error_handling import Location
from starkware.cairo.lang.compiler.preprocessor.auxiliary_info_collector import (  # noqa: E501
    AuxiliaryInfoCollector,
)
from starkware.cairo.lang.compiler.scoped_name import ScopedName


@dataclass
class ContractFunctionInfo:
    name: str
    start_pc: int
    end_pc: Optional[int] = None


class ContractFunctionInfoCollector(AuxiliaryInfoCollector):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._function_info: Dict[ScopedName, ContractFunctionInfo] = {}
        # We use a stack to keep track of the current function name, since
        # start_function_info might be called multiple times in succession in
        # case of nested scopes, and finish_function_info does not receive a
        # function name.
        self._function_name_stack: List[ScopedName] = []

    @classmethod
    def create(
        cls, *args: Any, **kwargs: Any,
    ) -> 'ContractFunctionInfoCollector':
        return cls(*args, **kwargs)

    def start_function_info(
        self, name: str, start_pc: int, *args: Any, **kwargs: Any,
    ) -> None:
        scoped_name = ScopedName.from_string(name)
        assert scoped_name not in self._function_info

        self._function_name_stack.append(scoped_name)
        function_info = ContractFunctionInfo(
            name=scoped_name.path[-1],
            start_pc=start_pc,
        )
        self._function_info[scoped_name] = function_info

    def finish_function_info(self, end_pc: int) -> None:
        function_name = self._function_name_stack.pop()
        self._function_info[function_name].end_pc = end_pc

    def get_function_info(
        self, scoped_name: Optional[ScopedName] = None,
    ) -> ContractFunctionInfo:
        return self._function_info[scoped_name]

    def add_assert_eq(self, lhs: Expression, rhs: Expression) -> None:
        pass

    def start_compound_assert_eq(
        self, lhs: Expression, rhs: Expression,
    ) -> None:
        pass

    def finish_compound_assert_eq(self) -> None:
        pass

    def add_reference(
        self,
        name: ScopedName,
        expr: Expression,
        identifier_loc: Optional[Location],
    ) -> None:
        pass

    def start_temp_var(
        self,
        name: ScopedName,
        expr: Expression,
        identifier_loc: Optional[Location],
    ) -> None:
        pass

    def finish_temp_var(self) -> None:
        pass

    def start_func_call(self, name: str, args: List[Expression]) -> None:
        pass

    def finish_func_call(self) -> None:
        pass

    def start_tail_call(self, args: List[Expression]) -> None:
        pass

    def finish_tail_call(self) -> None:
        pass

    def add_func_ret_vars(self, ret_vars: List[str]) -> None:
        pass

    def start_return(self) -> None:
        pass

    def finish_return(self, exprs: List[ExprAssignment]) -> None:
        pass

    def record_label(self, label_full_name: str) -> None:
        pass

    def record_jump_to_labeled_instruction(
        self,
        label_name: str,
        condition: Optional[Expression],
        current_pc: int,
        pc_dest: Optional[int] = None,
    ) -> None:
        pass

    def start_if(
        self, expr_a: Expression, expr_b: Expression, cond_eq: bool,
    ) -> None:
        pass

    def end_if(self) -> None:
        pass

    def add_add_ap(self, expr: Expression) -> None:
        pass

    def add_const(self, name: ScopedName, val: int) -> None:
        pass
