import os

class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///voting_system.db'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
