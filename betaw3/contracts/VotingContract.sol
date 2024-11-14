// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingContract {
    address public admin;
    mapping(address => bool) public hasVoted;
    mapping(address => bool) public whitelistedVoters; // Lista blanca de votantes
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

    // Agregar un votante a la lista blanca
    function addVoterToWhitelist(address _voter) public onlyAdmin {
        whitelistedVoters[_voter] = true;
    }

    // Quitar un votante de la lista blanca
    function removeVoterFromWhitelist(address _voter) public onlyAdmin {
        whitelistedVoters[_voter] = false;
    }

    // Verificar si un votante está en la lista blanca
    function isWhitelisted(address _voter) public view returns (bool) {
        return whitelistedVoters[_voter];
    }

    // Emitir un voto
    function castVote() public {
        require(votingActive, "Voting is not active.");
        require(whitelistedVoters[msg.sender], "You are not whitelisted to vote.");
        require(!hasVoted[msg.sender], "You have already voted.");

        hasVoted[msg.sender] = true;
        totalVotes += 1;
    }

    // Finalizar la votación
    function endVoting() public onlyAdmin {
        votingActive = false;
    }
}
