import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BLOCKCHAIN_URL = os.getenv('BLOCKCHAIN_URL', 'http://127.0.0.1:7545')
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '0xYourContractAddress')  # Dirección del contrato desplegado
