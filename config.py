from sqlalchemy import create_engine

class Config(object):
    SECRET_KEY ="CLAVESECRETA"
    SESSION_COOKIE_SECURE=False
    
class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/threadline"
    SQLALCHEMY_TRACK_MODIFICATIONS=False