from brownie import SwapToken, TokenFarm, config, network
from web3 import Web3

from scripts.config_dump_json import dump_config_json
from scripts.helpers import get_account, get_contract

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_swap_token(dump_json_config=False):
    account = get_account()
    swap_token = SwapToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(
        swap_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    tx = swap_token.transfer(
        token_farm.address, swap_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)
    # swap_token, weth, fau_token
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    dict_of_allowed_tokens = {
        swap_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
    }
    add_allowed_tokens(token_farm, dict_of_allowed_tokens, account)
    if dump_json_config:
        dump_config_json()
    return token_farm, swap_token


def add_allowed_tokens(token_farm, dict_of_allowed_tokens: dict, account):
    for token, price_feed in dict_of_allowed_tokens.items():
        tx = token_farm.addAllowedTokens(token.address, {"from": account})
        tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(
            token.address, price_feed, {"from": account}
        )
        set_tx.wait(1)
    return token_farm


def main():
    deploy_token_farm_and_swap_token(dump_json_config=True)
