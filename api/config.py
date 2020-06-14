import os

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = os.getenv('APP_DEBUG')
PORT = os.getenv('APP_PORT')
HOST = os.getenv('APP_HOST')
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICTIONS = True
SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
