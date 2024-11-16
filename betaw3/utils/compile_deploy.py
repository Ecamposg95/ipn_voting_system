import json
from solcx import compile_standard, install_solc
from web3 import Web3
import os

# Instalar versión de Solidity
print("Instalando Solidity Compiler...")
install_solc("0.8.0")

def compile_contract():
    print("Compilando el contrato...")
    contract_path = os.path.join(os.path.dirname(__file__), "../contracts/VotingContract.sol")
    
    if not os.path.exists(contract_path):
        print(f"Error: No se encontró el archivo {contract_path}.")
        return None

    with open(contract_path, "r") as file:
        contract_source_code = file.read()

    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {"VotingContract.sol": {"content": contract_source_code}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}}}
    }, solc_version="0.8.0")

    output_path = os.path.join(os.path.dirname(__file__), "../contracts/VotingContract.json")
    with open(output_path, "w") as file:
        json.dump(compiled_sol, file)
    print(f"Contrato compilado y guardado en {output_path}.")
    return compiled_sol

def deploy_contract(w3, compiled_contract):
    print("Desplegando el contrato...")
    abi = compiled_contract["contracts"]["VotingContract.sol"]["VotingContract"]["abi"]
    bytecode = compiled_contract["contracts"]["VotingContract.sol"]["VotingContract"]["evm"]["bytecode"]["object"]

    # Definir la cuenta desde la que se enviará la transacción
    account = w3.eth.accounts[0]  # Usa la primera cuenta de Ganache
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Crear y enviar la transacción desde la cuenta especificada
    tx_hash = contract.constructor().transact({'from': account})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Contrato desplegado en la dirección: {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

if __name__ == "__main__":
    # Conéctate a la blockchain
    blockchain_url = os.getenv("BLOCKCHAIN_URL", "http://127.0.0.1:7545")
    print(f"Conectando a la blockchain en {blockchain_url}...")
    w3 = Web3(Web3.HTTPProvider(blockchain_url))
    
    if w3.is_connected():
        print("Conexión exitosa a la blockchain.")
        compiled_contract = compile_contract()
        if compiled_contract:
            contract_address = deploy_contract(w3, compiled_contract)
            print(f"Actualiza el archivo .env con CONTRACT_ADDRESS={contract_address}")
    else:
        print("No se pudo conectar a la blockchain. Verifica la URL.")
