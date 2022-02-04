// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract SwapToken is ERC20 {
    constructor() public ERC20("Swap Token", "SWAP") {
        _mint(msg.sender, 1e6 ether);
    }
}
