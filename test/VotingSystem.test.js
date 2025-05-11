const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("VotingSystem", () => {
  let voting, owner, admin, user1, user2;

  beforeEach(async () => {
    [owner, admin, user1, user2] = await ethers.getSigners();

    const Voting = await ethers.getContractFactory("VotingSystem");
    voting = await Voting.deploy();
  });

  it("should set admin only once", async () => {
    await voting.connect(owner).setAdmin(admin.address);
    expect(await voting.admin()).to.equal(admin.address);

    // Should fail if trying to reset admin
    await expect(voting.connect(user1).setAdmin(user2.address)).to.be.revertedWith("Admin already set");
  });

  it("admin should create a voting session", async () => {
    await voting.connect(owner).setAdmin(admin.address);

    const candidates = ["Alice", "Bob"];
    const duration = 60; // 1 min
    await expect(voting.connect(admin).createSession("Election 1", candidates, duration))
      .to.emit(voting, "SessionCreated");

    const session = await voting.sessions(0);
    expect(session.title).to.equal("Election 1");
    expect(session.isActive).to.be.true;
  });

  it("non-admin cannot create session", async () => {
    await voting.connect(owner).setAdmin(admin.address);
    const candidates = ["Alice", "Bob"];
    await expect(
      voting.connect(user1).createSession("Fake Election", candidates, 60)
    ).to.be.revertedWith("Only admin can perform this action");
  });

  it("user should vote only once", async () => {
    await voting.connect(owner).setAdmin(admin.address);
    await voting.connect(admin).createSession("TestVote", ["A", "B"], 100);

    await voting.connect(user1).vote(0, 0); // vote for A
    await expect(voting.connect(user1).vote(0, 1)).to.be.revertedWith("You have already voted");
  });

  it("should not allow voting after session ends", async () => {
    await voting.connect(owner).setAdmin(admin.address);
    await voting.connect(admin).createSession("ShortVote", ["X", "Y"], 1); // 1 sec

    // Wait 2 seconds
    await new Promise((r) => setTimeout(r, 2000));

    await expect(voting.connect(user1).vote(0, 0)).to.be.revertedWith("Voting session has ended");
  });

  it("admin can end session early", async () => {
    await voting.connect(owner).setAdmin(admin.address);
    await voting.connect(admin).createSession("EndEarly", ["A", "B"], 100);
    await voting.connect(admin).endSession(0);

    const session = await voting.sessions(0);
    expect(session.isActive).to.equal(false);
  });

  it("admin can release results", async () => {
    await voting.connect(owner).setAdmin(admin.address);
    await voting.connect(admin).createSession("Results", ["A", "B"], 100);
    await voting.connect(admin).releaseResults(0);

    const session = await voting.sessions(0);
    expect(session.resultsReleased).to.be.true;
  });
});
