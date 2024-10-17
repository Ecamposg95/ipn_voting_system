pragma solidity ^0.8.0;

contract VoterRegistration {
    address public admin;
    mapping(address => bool) public registeredVoters;

    constructor() {
        admin = msg.sender;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    function registerVoter(address _voter) public onlyAdmin {
        registeredVoters[_voter] = true;
    }

    function isRegistered(address _voter) public view returns (bool) {
        return registeredVoters[_voter];
    }
}
