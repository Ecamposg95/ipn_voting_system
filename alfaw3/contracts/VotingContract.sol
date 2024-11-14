// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingContract {
    struct Candidate {
        uint id;
        string name;
        uint voteCount;
    }

    mapping(uint => Candidate) public candidates;
    mapping(address => bool) public voters;
    uint public candidatesCount;
    uint public totalVotes;

    address public admin;

    constructor() {
        admin = msg.sender;
    }

    function addCandidate(string memory _name) public {
        require(msg.sender == admin, "Only admin can add candidates.");
        candidatesCount++;
        candidates[candidatesCount] = Candidate(candidatesCount, _name, 0);
    }

    function vote(uint _candidateId) public {
        require(!voters[msg.sender], "You have already voted.");
        require(_candidateId > 0 && _candidateId <= candidatesCount, "Invalid candidate.");
        
        voters[msg.sender] = true;
        candidates[_candidateId].voteCount++;
        totalVotes++;
    }

    function getWinner() public view returns (string memory) {
        uint winningVoteCount = 0;
        string memory winnerName = "";
        for (uint i = 1; i <= candidatesCount; i++) {
            if (candidates[i].voteCount > winningVoteCount) {
                winningVoteCount = candidates[i].voteCount;
                winnerName = candidates[i].name;
            }
        }
        return winnerName;
    }
}
