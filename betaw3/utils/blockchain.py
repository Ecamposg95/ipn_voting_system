import json
from web3 import Web3
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

class BlockchainHandler:
    def __init__(self):
        # Conectar a la blockchain usando la URL de blockchain en el archivo .env
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_URL")))
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        
        # Cargar el ABI del contrato desde el archivo JSON compilado
        with open("contracts/VotingContract.json") as f:
            contract_data = json.load(f)
            self.contract_abi = contract_data["contracts"]["VotingContract.sol"]["VotingContract"]["abi"]
        
        # Crear la instancia del contrato
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)

    def register_voter(self, voter_address):
        account = self.w3.eth.accounts[0]
        txn = self.contract.functions.registerVoter(voter_address).transact({'from': account})
        return self.w3.eth.wait_for_transaction_receipt(txn)

    def cast_vote(self):
        account = self.w3.eth.accounts[0]
        txn = self.contract.functions.castVote().transact({'from': account})
        return self.w3.eth.wait_for_transaction_receipt(txn)
