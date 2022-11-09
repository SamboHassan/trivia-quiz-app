import os
from dotenv import load_dotenv


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_TRIVIA_TEST = os.getenv("DB_TRIVIA_TEST")

# development config
class Config(object):

    SECRET_KEY = os.urandom(32)
    # Grabs the folder where the script runs.
    basedir = os.path.abspath(os.path.dirname(__file__))

    # set defaults
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    database_path = "postgresql://{}:{}@{}/{}".format(
        DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
    )

    SQLALCHEMY_DATABASE_URI = database_path


# Production config
class ProductionConfig(Config):
    pass


# Testing config
class TestingConfig(Config):
    TESTING = True
    database_path = "postgresql://{}:{}@{}/{}".format(
        DB_USER, DB_PASSWORD, DB_HOST, DB_TRIVIA_TEST
    )
