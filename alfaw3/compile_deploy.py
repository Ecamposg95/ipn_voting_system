from web3 import Web3
import json
from solcx import compile_source, install_solc, set_solc_version

# Instalar y configurar la versión de solc
install_solc("0.8.0")
set_solc_version("0.8.0")

# Conectar a la blockchain (Ganache local)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Compilar el contrato
with open('./contracts/VotingContract.sol', 'r') as file:
    contract_source_code = file.read()

compiled_sol = compile_source(contract_source_code)
contract_interface = compiled_sol['<stdin>:VotingContract']

# Desplegar el contrato
VotingContract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
tx_hash = VotingContract.constructor().transact({'from': w3.eth.accounts[0]})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Guardar dirección y ABI
contract_address = tx_receipt.contractAddress
abi = contract_interface['abi']
with open('VotingContract_abi.json', 'w') as abi_file:
    json.dump(abi, abi_file)

print("Contrato desplegado en:", contract_address)
