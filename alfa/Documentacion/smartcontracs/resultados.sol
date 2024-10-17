pragma solidity ^0.8.0;

contract VotingResults {
    address public admin;
    mapping(uint256 => uint256) public finalResults;
    bool public resultsFinalized;

    constructor() {
        admin = msg.sender;
        resultsFinalized = false;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    function finalizeResults(uint256[] memory candidateIds, uint256[] memory candidateVotes) public onlyAdmin {
        require(!resultsFinalized, "Results are already finalized");
        for (uint256 i = 0; i < candidateIds.length; i++) {
            finalResults[candidateIds[i]] = candidateVotes[i];
        }
        resultsFinalized = true;
    }

    function getFinalResult(uint256 candidateId) public view returns (uint256) {
        return finalResults[candidateId];
    }
}
