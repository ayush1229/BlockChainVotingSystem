from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to Sepolia or any Ethereum provider
provider_url = os.getenv("SEPOLIA_RPC_URL")
private_key = os.getenv("PRIVATE_KEY")
public_address = Web3.to_checksum_address(os.getenv("PUBLIC_ADDRESS"))  # Use the correct address

w3 = Web3(Web3.HTTPProvider(provider_url))

# Load ABI
with open(os.path.join(os.path.dirname(__file__), "app/static/contracts/contracts/Voting.sol/VotingSystem.json")) as f:
    contract_data = json.load(f)

voting_abi = contract_data["abi"]
voting_contract_address = Web3.to_checksum_address("0x39a18C3b330C4b14981dEBdF1D347c7a5727b61D")  # Replace with actual deployed address

voting_contract = w3.eth.contract(address=voting_contract_address, abi=voting_abi)

# Load NFT ABI and Address (You'll need to deploy your NFT contract and get its details)
# IMPORTANT: Replace with the actual path to your NFT contract ABI and deployed address
try:
    with open("app/static/contracts/VotingNFT.json") as f: # Replace with your NFT ABI path
        nft_contract_data = json.load(f)
    nft_abi = nft_contract_data["abi"]
    nft_contract_address = Web3.to_checksum_address("YOUR_NFT_CONTRACT_ADDRESS") # Replace with your NFT contract address
    nft_contract = w3.eth.contract(address=nft_contract_address, abi=nft_abi)
except FileNotFoundError:
    print("Warning: NFT contract ABI not found. Minting functionality will not work.")

# Helper: Send a transaction
def send_transaction(function, account_address):
    nonce = w3.eth.get_transaction_count(account_address)

    tx = function.build_transaction({
        'from': account_address,
        'nonce': nonce,
        'gas': 3000000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 11155111  # Sepolia chain ID
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)


# ========== EXAMPLES ==========

# 1. Set Admin (only once)
def set_admin(admin_address):
    admin_address = Web3.to_checksum_address(admin_address)
    func = voting_contract.functions.setAdmin(admin_address)
    return send_transaction(func, public_address)

# 2. Create a Voting Session
def create_session(title, candidate_names, duration_in_seconds):
    func = voting_contract.functions.createSession(title, candidate_names, duration_in_seconds)
    return send_transaction(func, public_address)

# 3. Mint a voting NFT
def mint_nft(to_address, session_id):
    to_address = Web3.to_checksum_address(to_address)
    func = nft_contract.functions.mintVotingNFT(to_address, session_id)
    return send_transaction(func, public_address)

# 3. Vote (as a user)
def vote(session_id, candidate_index, voter_address, voter_private_key):
    voter_address = Web3.to_checksum_address(voter_address)
    nonce = w3.eth.get_transaction_count(voter_address)
    tx = contract.functions.vote(session_id, candidate_index).build_transaction({
        'from': voter_address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 11155111
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=voter_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)

# 4. End session
def end_session(session_id):
    func = voting_contract.functions.endSession(session_id)
    return send_transaction(func, public_address)

# 5. Release results
def release_results(session_id):
    func = voting_contract.functions.releaseResults(session_id)
    return send_transaction(func, public_address)

# 6. Read-only: Get candidates
def get_candidates(session_id): # NOTE: This function might need adjustment based on how candidates are stored/retrieved on-chain
    return voting_contract.functions.getCandidates(session_id).call()

# 7. Read-only: Has user voted
def has_user_voted(session_id, user_address):
    return voting_contract.functions.hasVoted(session_id, Web3.to_checksum_address(user_address)).call()
