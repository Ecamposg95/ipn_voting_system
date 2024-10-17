pragma solidity ^0.8.0;

contract Voting {
    address public admin;
    mapping(address => bool) public hasVoted;
    mapping(uint256 => uint256) public votes;

    constructor() {
        admin = msg.sender;
    }

    modifier onlyRegisteredVoter() {
        require(hasVoted[msg.sender] == false, "Voter has already voted");
        _;
    }

    function vote(uint256 candidateId) public onlyRegisteredVoter {
        hasVoted[msg.sender] = true;
        votes[candidateId] += 1;
    }

    function getVotes(uint256 candidateId) public view returns (uint256) {
        return votes[candidateId];
    }
}
