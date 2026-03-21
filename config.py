from sqlalchemy import create_engine

class Config(object):
    SECRET_KEY ="CLAVESECRETA"
    SESSION_COOKIE_SECURE=False
    
class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Potrerodelasierra118@127.0.0.1/thredline"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

