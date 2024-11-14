import json
from utils.blockchain import BlockchainHandler

def load_whitelist(blockchain: BlockchainHandler):
    try:
        with open("whitelist.json") as f:
            data = json.load(f)
            for address in data["addresses"]:
                tx_hash = blockchain.contract.functions.addVoterToWhitelist(address).transact({'from': blockchain.w3.eth.accounts[0]})
                blockchain.w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"Dirección {address} agregada a la lista blanca.")
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'whitelist.json'. Asegúrate de que el archivo existe.")
    except Exception as e:
        print(f"Error al cargar la lista blanca: {e}")
