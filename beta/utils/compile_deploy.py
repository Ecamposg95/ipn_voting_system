import json
from solcx import compile_standard, install_solc
from web3 import Web3
import os

# Instalar versión de Solidity
print("Instalando Solidity Compiler...")
install_solc("0.8.0")

def compile_contract():
    print("Compilando el contrato...")
    with open("../contracts/VotingContract.sol", "r") as file:
        contract_source_code = file.read()

    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {"VotingContract.sol": {"content": contract_source_code}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}}}
    }, solc_version="0.8.0")

    with open("../contracts/VotingContract.json", "w") as file:
        json.dump(compiled_sol, file)
    print("Contrato compilado y guardado en VotingContract.json.")

def deploy_contract(w3):
    print("Desplegando el contrato...")
    with open("../contracts/VotingContract.json", "r") as file:
        compiled_contract = json.load(file)

    abi = compiled_contract["contracts"]["VotingContract.sol"]["VotingContract"]["abi"]
    bytecode = compiled_contract["contracts"]["VotingContract.sol"]["VotingContract"]["evm"]["bytecode"]["object"]

    # Definir la cuenta desde la que se enviará la transacción
    account = w3.eth.accounts[0]  # Usa la primera cuenta de Ganache
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Crear y enviar la transacción desde la cuenta especificada
    tx_hash = contract.constructor().transact({'from': account})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)  # Método corregido
    print(f"Contrato desplegado en la dirección: {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress



if __name__ == "__main__":
    # Conéctate a la blockchain
    blockchain_url = os.getenv("BLOCKCHAIN_URL", "http://127.0.0.1:7545")
    print(f"Conectando a la blockchain en {blockchain_url}...")
    w3 = Web3(Web3.HTTPProvider(blockchain_url))
    
    if w3.is_connected():  # Cambiado a is_connected()
        print("Conexión exitosa a la blockchain.")
        compile_contract()
        contract_address = deploy_contract(w3)
        print(f"Actualiza el archivo .env con CONTRACT_ADDRESS={contract_address}")
    else:
        print("No se pudo conectar a la blockchain. Verifica la URL.")
