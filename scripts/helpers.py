from typing import Optional

from brownie import (
    Contract,
    MockFAU,
    MockV3Aggregator,
    MockWETH,
    accounts,
    config,
    network,
)
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = {
    "development",
    "ganache-local",
    "mainnet-fork",
}
INITIAL_PRICE_FEED_VALUE = int(2_000e18)


def get_account(index: Optional[int] = None, id: Optional[str] = None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    else:
        return accounts.load("meta")


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "fau_token": MockFAU,
    "weth_token": MockWETH,
}


def get_contract(contract_name: str):
    """
    This function will grab the contract addresses from the brownie config
    if defined, otherwise it will deploy a mock version of that contract,
    and return that mock contract.

    Args:
        contract_name (string)

    Returns:
        brownie.network.contract.ProjectContract: The most recently
        deployed version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )

    return contract


def deploy_mocks(decimals=18, initial_price=INITIAL_PRICE_FEED_VALUE):
    """
    Use this script if you want to deploy mocks to a testnet
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()

    print("Deploying Mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_price, {"from": account}
    )
    print(f"Deployed to {mock_price_feed.address}")
    print("Deploying Mock FAU...")
    fau_token = MockFAU.deploy({"from": account})
    print(f"Deployed to {fau_token.address}")
    print("Dploying Mock WETH...")
    weth_token = MockWETH.deploy({"from": account})
    print(f"Deployed to {weth_token.address}")
    print("All done!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=Web3.toWei(0.3, "ether")
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    funding_tx = link_token.transfer(contract_address, amount, {"from": account})
    funding_tx.wait(1)
    print(f"Funded {contract_address}")
    return funding_tx
