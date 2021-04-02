import logging
import re

from elasticsearch_dsl import Search, connections
from pyArango.connection import Connection

from scicopia.config import read_config
from scicopia.exceptions import ConfigError, DBError, SearchError


class Config:
    config = read_config()

    if not "secret_key" in config:
        raise ConfigError("Setting missing in config file: 'secret_key'.")
    SECRET_KEY = config["secret_key"]

    if not "mailusername" in config:
        raise ConfigError("Setting missing in config file: 'mailusername'.")
    if not "mailpassword" in config:
        raise ConfigError("Setting missing in config file: 'mailpassword'.")
    if not "mailsubjectprefix" in config:
        raise ConfigError("Setting missing in config file: 'mailsubjectprefix'.")
    if not "mailsender" in config:
        raise ConfigError("Setting missing in config file: 'mailsender'.")
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config["mailusername"]
    MAIL_PASSWORD = config["mailpassword"]
    MAIL_SUBJECT_PREFIX = config["mailsubjectprefix"]
    MAIL_SENDER = config["mailsender"]

    URL_MATCHER = re.compile(r"((https?|ftp)://[^\s/$.?#].[^\s]+[^\s\.])")

    if not "es_hosts" in config:
        raise ConfigError("Setting missing in config file: 'es_hosts'.")
    if not "index" in config:
        raise ConfigError("Setting missing in config file: 'index'.")
    if not "fields" in config:
        raise ConfigError("Setting missing in config file: 'fields'.")
    conn = connections.create_connection(hosts=config["es_hosts"])
    if not conn.ping():
        raise SearchError("Connection to the Elasticsearch server failed.")
    search = Search(using=conn)
    SEARCH = search.index(config["index"])
    FIELDS = config["fields"]

    if not "username" in config:
        raise ConfigError("Setting missing in config file: 'username'.")
    if not "password" in config:
        raise ConfigError("Setting missing in config file: 'password'.")
    try:
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
    except:
        raise DBError(f"Connection to the ArangoDB server failed.")

    if not "database" in config:
        raise ConfigError("Setting missing in config file: 'database'.")
    if arangoconn.hasDatabase(config["database"]):
        DB = arangoconn[config["database"]]
    else:
        raise DBError(f"Database '{config['database']}' not found.")

    if not "documentcollection" in config:
        raise ConfigError("Setting missing in config file: 'documentcollection'.")
    COLLECTIONNAME = config["documentcollection"]
    if DB.hasCollection(COLLECTIONNAME):
        COLLECTION = DB[COLLECTIONNAME]
    else:
        raise DBError(f"Collection '{COLLECTIONNAME}' not found.")

    if not "pdfcollection" in config:
        raise ConfigError("Setting missing in config file: 'pdfcollection'.")
    PDFCOLLECTIONNAME = config["pdfcollection"]
    if DB.hasCollection(PDFCOLLECTIONNAME):
        PDFCOLLECTION = DB[PDFCOLLECTIONNAME]
    else:
        raise DBError(f"Collection '{PDFCOLLECTIONNAME}' not found.")

    if not "usercollection" in config:
        raise ConfigError("Setting missing in config file: 'usercollection'.")
    USERCOLLECTIONNAME = config["usercollection"]
    if DB.hasCollection(USERCOLLECTIONNAME):
        USERCOLLECTION = DB[USERCOLLECTIONNAME]
    else:
        USERCOLLECTION = DB.createCollection(name=config["usercollection"])

    if ("nodecollections" in config and "edgecollections" in config
        and isinstance(config["nodecollections"], list) and len(config["nodecollections"][0]) > 0
        and isinstance(config["edgecollections"], list) and len(config["edgecollections"][0]) > 0):
        NODECOLLECTIONS = config["nodecollections"]
        EDGECOLLECTIONS = config["edgecollections"]
        DASH = True
    else:
        DASH = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
} 
