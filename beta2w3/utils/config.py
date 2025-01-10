import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URI = os.getenv("DATABASE_URI")
    BLOCKCHAIN_URL = os.getenv("BLOCKCHAIN_URL")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///betaw3.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
