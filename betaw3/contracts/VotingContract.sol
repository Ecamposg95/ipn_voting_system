// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingContract {
    address public admin;
    mapping(address => bool) public hasVoted;
    mapping(address => bool) public registeredVoters;
    uint public totalVotes;
    bool public votingActive;

    constructor() {
        admin = msg.sender;
        votingActive = true;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this function.");
        _;
    }

    function registerVoter(address _voter) public onlyAdmin {
        registeredVoters[_voter] = true;
    }

    function castVote() public {
        require(votingActive, "Voting is not active.");
        require(registeredVoters[msg.sender], "You are not registered to vote.");
        require(!hasVoted[msg.sender], "You have already voted.");

        hasVoted[msg.sender] = true;
        totalVotes += 1;
    }

    function endVoting() public onlyAdmin {
        votingActive = false;
    }
}
