import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1']
