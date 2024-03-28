import os
import platform
from pathlib import Path
from flask import current_app

# base directory
BASE_DIR = current_app.config.get("BASE_DIR")  # ./e2d-flask

# flask
# SECRET_KEY = b'the human story...'
SECRET_KEY = os.urandom(10)

# database
database_type = current_app.config["DATABASE_TYPE"]

if database_type in ["SQLite3", "MongoDB"]:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///database/db_admin.sqlite3'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.getcwd()}/database/db_admin.sqlite3'  # absolute path
    # SQLALCHEMY_DATABASE_URI = 'mongodb://user1:user1@127.0.0.1:27017/db_admin'  # unsupported

elif database_type in ["PostgreSQL"]:
    if "Windows" in platform.system():
        # PC
        SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user1:user1@127.0.0.1:5432/db_admin'
    else:
        # HEROKU
        # uri = os.getenv("DATABASE_URL")
        # if uri and uri.startswith("postgres://"):
        #     uri = uri.replace("postgres://", "postgresql://", 1)
        #     SQLALCHEMY_DATABASE_URI = uri

        # WSL Ubuntu
        SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user1:user1@127.0.0.1:5432/db_admin'
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///database/db_admin.sqlite3'  # if use sqlite3 for db_admin
else:
    pass

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # console log on / off

E2D_EXCEL_MAX_RECORDS = 500_000

# topview
APPLICATION_TITLE = "Excel to Database application"
LOG_FILE = Path(BASE_DIR, 'log/app.log')
LOG_FILE_MAXBYTES = 10_000_000  # 10MB
