from web3 import Web3
import json

class ContractHandler:
    def __init__(self, blockchain_url, contract_address, abi):
        self.w3 = Web3(Web3.HTTPProvider(blockchain_url))
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        self.account = self.w3.eth.accounts[0]  # Cuenta para firmar transacciones

    def get_admin(self):
        return self.contract.functions.admin().call()  # Retorna la dirección del administrador

    def change_admin(self, new_admin_address):
        # Función para cambiar al administrador
        tx = self.contract.functions.changeAdmin(new_admin_address).buildTransaction({
            'from': self.account,
            'gas': 2000000,
            'gasPrice': self.w3.toWei('20', 'gwei'),
            'nonce': self.w3.eth.getTransactionCount(self.account),
        })
        signed_tx = self.w3.eth.account.signTransaction(tx, private_key='your_private_key')
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_hash

    def submit_vote(self, votacion_id, opcion_id):
        tx = self.contract.functions.vote(votacion_id, opcion_id).buildTransaction({
            'from': self.account,
            'gas': 2000000,
            'gasPrice': self.w3.toWei('20', 'gwei'),
            'nonce': self.w3.eth.getTransactionCount(self.account),
        })
        signed_tx = self.w3.eth.account.signTransaction(tx, private_key='your_private_key')
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_hash
