from starkware.cairo.lang.compiler.scoped_name import ScopedName

from pytest_cairo.info_collector import (
    ContractFunctionInfo, ContractFunctionInfoCollector,
)


def test_contract_function_info_collector() -> None:
    info_collector = ContractFunctionInfoCollector.create()

    contract_function_info_1 = ContractFunctionInfo(
        name='func1',
        start_pc=0,
    )
    scoped_name = ScopedName.from_string(contract_function_info_1.name)

    info_collector.start_function_info(
        contract_function_info_1.name,
        contract_function_info_1.start_pc,
    )

    actual = info_collector.get_function_info(scoped_name)
    expected = contract_function_info_1
    assert actual == expected

    contract_function_info_1.end_pc = 10

    info_collector.finish_function_info(contract_function_info_1.end_pc)

    actual = info_collector.get_function_info(scoped_name)
    expected = contract_function_info_1
    assert actual == expected


def test_contract_function_info_collector_nested() -> None:
    # Test whether nested functions are handled correctly. In those cases
    # start_function_info is called for a second function, before
    # finish_function_info is called for the first function.
    #
    # In this test the order goes:
    #   1. start_function_info for func1
    #   2. start_function_info for func2
    #   3. finish_function_info for func2
    #   4. finish_function_info for func1
    #
    info_collector = ContractFunctionInfoCollector.create()

    contract_function_info_1 = ContractFunctionInfo(
        name='func1',
        start_pc=0,
    )
    scoped_name_1 = ScopedName.from_string(contract_function_info_1.name)

    contract_function_info_2 = ContractFunctionInfo(
        name='func2',
        start_pc=2,
    )
    scoped_name_2 = ScopedName.from_string(contract_function_info_2.name)

    info_collector.start_function_info(
        contract_function_info_1.name,
        contract_function_info_1.start_pc,
    )

    actual = info_collector.get_function_info(scoped_name_1)
    expected = contract_function_info_1
    assert actual == expected

    info_collector.start_function_info(
        contract_function_info_2.name,
        contract_function_info_2.start_pc,
    )

    actual = info_collector.get_function_info(scoped_name_2)
    expected = contract_function_info_2
    assert actual == expected

    contract_function_info_2.end_pc = 8
    contract_function_info_1.end_pc = 10

    info_collector.finish_function_info(contract_function_info_2.end_pc)

    actual = info_collector.get_function_info(scoped_name_2)
    expected = contract_function_info_2
    assert actual == expected

    info_collector.finish_function_info(contract_function_info_1.end_pc)

    actual = info_collector.get_function_info(scoped_name_1)
    expected = contract_function_info_1
    assert actual == expected
