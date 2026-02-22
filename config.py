import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "super-secret-dev-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "gautam2002jha@gmail.com"
    MAIL_PASSWORD = "yetfjcxltnvqplza"
    MAIL_DEFAULT_SENDER = "gautam2002jha@gmail.com"

