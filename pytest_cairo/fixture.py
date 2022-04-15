from typing import Any

from pytest_cairo.function import ContractFunctionBase

FIXTURE_DECORATOR = 'fixture'


class FixtureFunction(ContractFunctionBase):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        # `invoke` instead of `call` since we want changes from fixtures to
        # be persisted in the state. This allows for setting up tests that
        # require contracts to be deployed, or changes to storage variables
        # etc.
        execution_info = self.invoke(*args, **kwargs)
        result = execution_info.result
        if len(result) == 0:
            # Tests request fixtures by including the fixture name as a
            # function argument, which requires defining a type, even though
            # fixture might not return a value. In this case we return 0 and
            # expect the function argument to be defined as a felt.
            return 0
        elif len(result) == 1:
            return result[0]
        else:
            raise Exception(
                f'Fixture {self.__name__} returns more than 1 value.')
