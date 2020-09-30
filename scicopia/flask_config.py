import logging
import re
from elasticsearch_dsl import connections, Search
from pyArango.connection import Connection
from .config import read_config


class Config:
    config = read_config()

    SECRET_KEY = config["secret_key"]

    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config["mailusername"]
    MAIL_PASSWORD = config["mailpassword"]
    Scicopia_MAIL_SUBJECT_PREFIX = "[Scicopia]"
    Scicopia_MAIL_SENDER = "Scicopia Admin"

    URL_MATCHER = re.compile(r"((https?|ftp)://[^\s/$.?#].[^\s]+[^\s\.])")

    conn = connections.create_connection(hosts=config["es_hosts"])
    search = Search(using=conn)
    SEARCH = search.index(config["index"])

    if "arango_url" in config:
        arangoconn = Connection(
            arangoURL=config["arango_url"],
            username=config["username"],
            password=config["password"],
        )
    else:
        arangoconn = Connection(
            username=config["username"], password=config["password"]
        )

    if arangoconn.hasDatabase(config["database"]):
        DB = arangoconn[config["database"]]
    else:
        logging.error(f"Database {config['database']} not found.")

    COLLECTIONNAME = config["collection"]
    if DB.hasCollection(COLLECTIONNAME):
        COLLECTION = DB[COLLECTIONNAME]
    else:
        logging.error(f"Collection {COLLECTIONNAME} not found.")

    USERCOLLECTIONNAME = config["usercollection"]
    if DB.hasCollection(USERCOLLECTIONNAME):
        USERCOLLECTION = DB[USERCOLLECTIONNAME]
    else:
        logging.error(f"Usercollection {USERCOLLECTIONNAME} not found.")
        
    NODECOLLECTIONS = config["nodecollections"]
    EDGECOLLECTIONS = config["edgecollections"]

    FIELDS = config["fields"]

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True


class TestingConfig(Config):
    DEBUG = False
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
} 
