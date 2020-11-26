from pyArango.connection import Connection
from pyArango.theExceptions import CreationError

from .config import read_config

config = read_config()

arangoconn = Connection(
    username=config["username"], password=config["password"]
)  # connection to ArangoDB
if arangoconn.hasDatabase(config["database"]):
    db = arangoconn[config["database"]]
else:
    db = arangoconn.createDatabase(name=config["database"])
if db.hasCollection(config["usercollection"]):
    coll = db[config["usercollection"]]
else:
    coll = db.createCollection(name=config["usercollection"])
