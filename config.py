import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "super-secret-dev-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "gpljha.medi@gmail.com"
    MAIL_PASSWORD = "exytrcneoxgwddoe"
    MAIL_DEFAULT_SENDER = "gpljha.medi@gmail.com"

