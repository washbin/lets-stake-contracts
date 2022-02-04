import pytest
from brownie import exceptions, network
from scripts.deploy import deploy_token_farm_and_swap_token
from scripts.helpers import (
    INITIAL_PRICE_FEED_VALUE,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
)


def test_set_price_feed_contract():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, swap_token = deploy_token_farm_and_swap_token()
    price_feed_address = get_contract("eth_usd_price_feed")
    # Act
    token_farm.setPriceFeedContract(
        swap_token.address, price_feed_address, {"from": account}
    )
    # Assert
    assert token_farm.tokenPriceFeedMapping(swap_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(
            swap_token.address, price_feed_address, {"from": non_owner}
        )


def test_stake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, swap_token = deploy_token_farm_and_swap_token()
    # Act
    swap_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, swap_token.address, {"from": account})
    # Assert
    assert (
        token_farm.stakingBalance(swap_token.address, account.address) == amount_staked
    )
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, swap_token


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, swap_token = test_stake_tokens(amount_staked)
    starting_balance = swap_token.balanceOf(account.address)
    # Act
    token_farm.issueTokens({"from": account})
    # Assert
    assert (
        swap_token.balanceOf(account.address)
        == starting_balance + INITIAL_PRICE_FEED_VALUE
    )
