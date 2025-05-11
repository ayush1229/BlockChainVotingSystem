const hre = require("hardhat");

async function main() {
  // Deploy the contract
  const VotingSystem = await hre.ethers.getContractFactory("VotingSystem");
  const votingSystem = await VotingSystem.deploy();
  
  await votingSystem.waitForDeployment();
  const contractAddress = await votingSystem.getAddress();

  console.log("VotingSystem deployed to:", contractAddress);
  console.log("IMPORTANT: Call setAdmin() after deployment to initialize the admin");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });