import logging
import re
from collections import Counter
from pickle import UnpicklingError

from elasticsearch_dsl import Search, connections
from pyArango.connection import Connection

from scicopia.app.parser.segmenter import QuerySplitter
from scicopia.config import read_config
from scicopia.exceptions import ConfigError, DBError, SearchError
from scicopia.utils.zstandard import zstd_unpickle

logger = logging.getLogger("scicopia")
logger.setLevel(logging.INFO)


class Config:
    config = read_config()

    if not "secret_key" in config:
        raise ConfigError("Setting missing in config file: 'secret_key'.")
    if len(config["secret_key"]) > 0:
        SECRET_KEY = config["secret_key"]
    else:
        raise ConfigError(
            "Set the secret_key on the application to something unique and secret."
        )

    URL_MATCHER = re.compile(r"((https?|ftp)://[^\s/$.?#].[^\s]+[^\s\.])")
    WHITESPACE = re.compile(r"\s{2,}")

    if not "es_hosts" in config:
        raise ConfigError("Setting missing in config file: 'es_hosts'.")
    if not "index" in config:
        raise ConfigError("Setting missing in config file: 'index'.")

    if not "fields" in config:
        raise ConfigError("Setting missing in config file: 'fields'.")
    CONN = connections.create_connection(hosts=config["es_hosts"])
    if not CONN.ping():
        raise SearchError("Connection to the Elasticsearch server failed.")
    if not CONN.indices.exists(index=config["index"]):
        raise SearchError("The given index does not exists.")
    search = Search(using=CONN)
    SEARCH = search.index(config["index"])
    if not "suggestions" in config:
        raise ConfigError("Setting missing in config file: 'suggestions'.")
    if not CONN.indices.exists(index=config["suggestions"]):
        raise SearchError("The given suggestions does not exists.")
    COMPLETION = search.index(config["suggestions"])
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

    if not "usercollection" in config:
        raise ConfigError("Setting missing in config file: 'usercollection'.")
    USERCOLLECTIONNAME = config["usercollection"]
    if DB.hasCollection(USERCOLLECTIONNAME):
        USERCOLLECTION = DB[USERCOLLECTIONNAME]
    else:
        USERCOLLECTION = DB.createCollection(name=config["usercollection"])
    
    if "query_ngrams" in config:
        try:
            completions = zstd_unpickle(config["query_ngrams"])
        except FileNotFoundError:
            raise ConfigError(f"File {config['query_ngrams']} does not exist.")
        except UnpicklingError as e:
            raise ConfigError(e)
        else:
            if not isinstance(completions, Counter):
                raise ConfigError(
                    f"Completions are of wrong type, expected Counter was {type(completions)}"
                )
        SEGMENTATION = QuerySplitter(completions)

    if (
        "nodecollections" in config
        and "edgecollections" in config
        and isinstance(config["nodecollections"], list)
        and len(config["nodecollections"][0]) > 0
        and isinstance(config["edgecollections"], list)
        and len(config["edgecollections"][0]) > 0
    ):
        NODECOLLECTIONS = config["nodecollections"]
        EDGECOLLECTIONS = config["edgecollections"]
        DASH = True
    else:
        DASH = False

    if not "mailusername" in config:
        raise ConfigError("Setting missing in config file: 'mailusername'.")
    if not "mailpassword" in config:
        raise ConfigError("Setting missing in config file: 'mailpassword'.")
    if not "mailsubjectprefix" in config:
        raise ConfigError("Setting missing in config file: 'mailsubjectprefix'.")
    if not "mailsender" in config:
        raise ConfigError("Setting missing in config file: 'mailsender'.")
    MAIL_SERVER = config["mailserver"]
    MAIL_PORT = config["mailport"]
    MAIL_USE_TLS = config["mailusetls"]
    MAIL_USERNAME = config["mailusername"]
    MAIL_PASSWORD = config["mailpassword"]
    MAIL_SUBJECT_PREFIX = config["mailsubjectprefix"]
    MAIL_SENDER = config["mailsender"]

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
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
