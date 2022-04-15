import pytest
from _pytest.outcomes import Failed
from starkware.starkware_utils.error_handling import StarkException

from pytest_cairo.function import ExpectedException, catch_expected_exceptions


def test_catch_expected_exceptions_max_len() -> None:
    with pytest.raises(ValueError, match='Currently one "raises" block'):
        catch_expected_exceptions([
            ExpectedException(0, 0, None),
            ExpectedException(0, 0, None),
        ]).__enter__()


def test_catch_expected_exceptions_only_starkexceptions() -> None:
    class NotAStarkException(Exception):
        pass

    with pytest.raises(NotAStarkException):
        with catch_expected_exceptions([ExpectedException(0, 0, None)]):
            raise NotAStarkException()


def test_catch_expected_exceptions_no_expected_exceptions() -> None:
    with pytest.raises(StarkException):
        with catch_expected_exceptions([]):
            raise StarkException(code=0)


def test_catch_expected_exceptions_expected_exceptions() -> None:
    expected_exception_without_message = ExpectedException(
        start_pc=0,
        end_pc=2,
        message=None,
    )

    with catch_expected_exceptions([expected_exception_without_message]):
        raise StarkException(code=0, message='Expected exception (pc=0:1)')

    with pytest.raises(StarkException):
        with catch_expected_exceptions([expected_exception_without_message]):
            raise StarkException(code=0, message='Expected exception (pc=0:3)')

    expected_exception_with_message = ExpectedException(
        start_pc=0,
        end_pc=2,
        message='Expected exception',
    )
    with catch_expected_exceptions([expected_exception_with_message]):
        raise StarkException(code=0, message='Expected exception at (pc=0:1)')

    with pytest.raises(StarkException):
        with catch_expected_exceptions([expected_exception_with_message]):
            raise StarkException(
                code=0, message='Exception we did not expect at (pc=0:1)')


def test_catch_expected_exceptions_did_not_raise() -> None:
    with pytest.raises(Failed):
        with catch_expected_exceptions([ExpectedException(0, 0, None)]):
            pass
