%lang starknet


@contract_interface
namespace IContract:
    func calculate_inverse(val : felt) -> (res : felt):
    end

    func only_owner() -> ():
    end
end
