pragma solidity ^0.8.0;

contract VotingAudit {
    address public admin;
    struct Vote {
        address voter;
        uint256 candidateId;
    }
    Vote[] public votes;
    mapping(address => bool) public hasVoted;

    constructor() {
        admin = msg.sender;
    }

    modifier onlyRegisteredVoter() {
        require(hasVoted[msg.sender] == false, "Voter has already voted");
        _;
    }

    function vote(uint256 candidateId) public onlyRegisteredVoter {
        votes.push(Vote(msg.sender, candidateId));
        hasVoted[msg.sender] = true;
    }

    function auditVotes() public view returns (Vote[] memory) {
        return votes;
    }
}
