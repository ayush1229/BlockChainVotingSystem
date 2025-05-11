// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingSystem {
    address public admin;
    uint public sessionCounter;

    constructor() {
        admin = address(0); // No admin by default
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    struct Candidate {
        string name;
        uint voteCount;
    }

    struct VotingSession {
        uint id;
        string title;
        uint endTime;
        bool isActive;
        bool resultsReleased;
        Candidate[] candidates;
        mapping(address => bool) hasVoted;
    }

    mapping(uint => VotingSession) public sessions;

    event AdminSet(address newAdmin);
    event SessionCreated(uint sessionId, string title, uint endTime);
    event Voted(uint sessionId, uint candidateIndex, address voter);
    event SessionEnded(uint sessionId);
    event ResultsReleased(uint sessionId);

    // Set the admin from backend after verification
    function setAdmin(address _admin) public {
        require(admin == address(0), "Admin already set");
        admin = _admin;
        emit AdminSet(_admin);
    }

    function createSession(
        string memory _title,
        string[] memory candidateNames,
        uint durationInSeconds
    ) public onlyAdmin {
        require(candidateNames.length > 0, "Need at least one candidate");

        VotingSession storage session = sessions[sessionCounter];
        session.id = sessionCounter;
        session.title = _title;
        session.endTime = block.timestamp + durationInSeconds;
        session.isActive = true;

        for (uint i = 0; i < candidateNames.length; i++) {
            session.candidates.push(Candidate(candidateNames[i], 0));
        }

        emit SessionCreated(sessionCounter, _title, session.endTime);
        sessionCounter++;
    }

    function vote(uint sessionId, uint candidateIndex) public {
        VotingSession storage session = sessions[sessionId];
        require(session.isActive, "Voting session is not active");
        require(block.timestamp < session.endTime, "Voting session has ended");
        require(!session.hasVoted[msg.sender], "You have already voted");
        require(candidateIndex < session.candidates.length, "Invalid candidate");

        session.candidates[candidateIndex].voteCount++;
        session.hasVoted[msg.sender] = true;

        emit Voted(sessionId, candidateIndex, msg.sender);
    }

    function endSession(uint sessionId) public onlyAdmin {
        VotingSession storage session = sessions[sessionId];
        require(session.isActive, "Session already ended");

        session.isActive = false;
        session.endTime = block.timestamp;

        emit SessionEnded(sessionId);
    }

    function releaseResults(uint sessionId) public onlyAdmin {
        VotingSession storage session = sessions[sessionId];
        require(!session.resultsReleased, "Results already released");

        session.resultsReleased = true;

        emit ResultsReleased(sessionId);
    }

    function getCandidates(uint sessionId) public view returns (Candidate[] memory) {
        VotingSession storage session = sessions[sessionId];
        Candidate[] memory list = new Candidate[](session.candidates.length);
        for (uint i = 0; i < session.candidates.length; i++) {
            list[i] = session.candidates[i];
        }
        return list;
    }

    function hasVoted(uint sessionId, address user) public view returns (bool) {
        return sessions[sessionId].hasVoted[user];
    }
}
// This contract allows an admin to create voting sessions, add candidates, and manage the voting process.