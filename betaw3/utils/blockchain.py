import json
from web3 import Web3
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

class BlockchainHandler:
    def __init__(self):
        # Conectar a la blockchain usando la URL de blockchain desde el archivo .env
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_URL")))
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        
        # Cargar el ABI del contrato desde el archivo JSON compilado
        self.contract_abi = self._load_contract_abi("contracts/VotingContract.json")
        
        # Crear la instancia del contrato
        if self.contract_abi:
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)
        else:
            print("Error: ABI del contrato no cargado correctamente.")

    def _load_contract_abi(self, filepath):
        """Carga el ABI del contrato desde el archivo JSON especificado."""
        try:
            with open(filepath) as f:
                contract_data = json.load(f)
                return contract_data["contracts"]["VotingContract.sol"]["VotingContract"]["abi"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"Error al cargar el ABI del contrato: {e}")
            return None

    def register_voter(self, voter_address):
        """Registra un votante en la lista blanca del contrato inteligente."""
        try:
            account = self.w3.eth.accounts[0]  # Usar la primera cuenta para ejecutar la transacción
            txn = self.contract.functions.addVoterToWhitelist(voter_address).transact({'from': account})
            receipt = self.w3.eth.wait_for_transaction_receipt(txn)
            print(f"Votante registrado con éxito: {voter_address}")
            return receipt
        except Exception as e:
            print(f"Error al registrar el votante: {e}")
            return None

    def cast_vote(self, voter_address):
        """Emite un voto usando la dirección del votante especificada."""
        try:
            txn = self.contract.functions.castVote().transact({'from': voter_address})
            receipt = self.w3.eth.wait_for_transaction_receipt(txn)
            print(f"Voto emitido con éxito desde la dirección: {voter_address}")
            return receipt
        except Exception as e:
            print(f"Error al emitir el voto: {e}")
            return None

    def end_voting(self):
        """Finaliza la votación desde la cuenta de administrador."""
        try:
            account = self.w3.eth.accounts[0]
            txn = self.contract.functions.endVoting().transact({'from': account})
            receipt = self.w3.eth.wait_for_transaction_receipt(txn)
            print("Votación finalizada con éxito.")
            return receipt
        except Exception as e:
            print(f"Error al finalizar la votación: {e}")
            return None

    def is_voter_whitelisted(self, voter_address):
        """Verifica si un votante está en la lista blanca."""
        try:
            is_whitelisted = self.contract.functions.whitelistedVoters(voter_address).call()
            print(f"Votante {voter_address} {'está' if is_whitelisted else 'no está'} en la lista blanca.")
            return is_whitelisted
        except Exception as e:
            print(f"Error al verificar la lista blanca del votante: {e}")
            return False

    def is_voting_active(self):
        """Verifica si la votación está activa."""
        try:
            return self.contract.functions.votingActive().call()
        except Exception as e:
            print(f"Error al verificar el estado de la votación: {e}")
            return False
