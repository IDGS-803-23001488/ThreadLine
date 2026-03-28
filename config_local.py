from sqlalchemy import create_engine

class Config(object):
    SECRET_KEY="ClaveSecreta"
    SESSION_COOKIE_SECURE=False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Potrerodelasierra118@127.0.0.1:3306/threadline'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "tu_correo@gmail.com"
    MAIL_PASSWORD = "tu_app_password"
    MAIL_DEFAULT_SENDER = "tu_correo@gmail.com"
