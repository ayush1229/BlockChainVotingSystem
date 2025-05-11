// This is a Hardhat configuration file for a project that uses the Hardhat framework.
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

// Validate environment variables
if (!process.env.SEPOLIA_RPC_URL) throw new Error("Missing SEPOLIA_RPC_URL in .env");
if (!process.env.PRIVATE_KEY) throw new Error("Missing PRIVATE_KEY in .env");

module.exports = {
  solidity: {
    version: "0.8.28",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [process.env.PRIVATE_KEY], // Array format (supports multiple keys)
      chainId: 11155111, // Explicit chainId for Sepolia
      gas: "auto", // Let Hardhat estimate
      gasPrice: "auto", // Let Hardhat estimate
      gasMultiplier: 1.2, // 20% buffer
    },
    localhost: { // Always include local testing
      url: "http://127.0.0.1:8545",
      chainId: 31337, // Hardhat default
    },
  },
  etherscan: {
    apiKey: {
      sepolia: process.env.ETHERSCAN_API_KEY, // Named key for Sepolia
    },
  },
  paths: {
    artifacts: "./project/app/static/contracts", // Match your Flask structure
  },
};