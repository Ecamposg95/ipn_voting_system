// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingContract {
    address public admin;
    mapping(address => bool) public hasVoted;
    mapping(address => bool) public whitelistedVoters;
    uint public totalVotes;
    bool public votingActive;

    event VoteCast(address voter);
    event VotingEnded();

    constructor() {
        admin = msg.sender;
        votingActive = true;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this function.");
        _;
    }

    function addVoterToWhitelist(address _voter) public onlyAdmin {
        whitelistedVoters[_voter] = true;
    }

    function addVotersToWhitelist(address[] memory _voters) public onlyAdmin {
        for (uint i = 0; i < _voters.length; i++) {
            whitelistedVoters[_voters[i]] = true;
        }
    }

    function removeVoterFromWhitelist(address _voter) public onlyAdmin {
        whitelistedVoters[_voter] = false;
    }

    function isWhitelisted(address _voter) public view returns (bool) {
        return whitelistedVoters[_voter];
    }

    function castVote() public {
        require(votingActive, "Voting is not active.");
        require(whitelistedVoters[msg.sender], "You are not whitelisted to vote.");
        require(!hasVoted[msg.sender], "You have already voted.");

        hasVoted[msg.sender] = true;
        totalVotes += 1;

        emit VoteCast(msg.sender);
    }

    function endVoting() public onlyAdmin {
        votingActive = false;
        emit VotingEnded();
    }

    function restartVoting() public onlyAdmin {
        require(!votingActive, "Voting is already active.");
        votingActive = true;
        totalVotes = 0;
    }

    function getVotingStatus() public view returns (bool) {
        return votingActive;
    }
}
