#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 7 12:54:23 2021

This module implements commonly used methods like connecting to
an ArangoDB instance.

- connect(Dict): Initial connection to an ArangoDB instance
                 using credentials

@author: tech
"""
from typing import Collection, Dict

from pyArango.connection import Connection
from pyArango.database import Database

from scicopia.exceptions import ConfigError, DBError


def connect(config: Dict) -> Connection:
    """
    Connect to the ArangoDB database.

    Parameters
    ----------
    config : Dict
        A configuration file containing the username and password
        necessary to connect to the database, as well as an optional
        parameter "arango_url", which provides a URL to the database,
        e.g. http://www.example.com:8529.

    Returns
    -------
    Connection
        A connection to the ArangoDB database

    Raises
    ------
    ConfigError
        If a required entry is missing in the config file
    DBError
        If the connection to the ArangoDB server failed
    """
    if not "username" in config:
        raise ConfigError("Setting missing in config file: 'username'.")
    if not "password" in config:
        raise ConfigError("Setting missing in config file: 'password'.")
    try:
        if "arango_url" in config:
            conn = Connection(
                arangoURL=config["arango_url"],
                username=config["username"],
                password=config["password"],
            )
        else:
            conn = Connection(username=config["username"], password=config["password"])
    except:
        raise DBError(f"Connection to the ArangoDB server failed.")
    else:
        return conn

def select_db(config: Dict, connection: Connection, create=False) -> Database:
    """
    Access a database inside an ArangoDB instance, after connecting
    to it.

    Parameters
    ----------
    config : Dict
        A configuration file containing the database settings,
        including a key-value pair "database", holding the
        name of the ArangoDB database to access.
    connection : Connection
        A connection to the ArangoDB instance
    create : bool, optional
        Create the database if it doesn't exist, by default False
    
    Returns
    -------
    Database
        A reference to the database mentioning the config file under
        "database", if it exists.

    Raises
    ------
    ConfigError
        If the "database" entry is missing in the config file.
    DBError
        If the database to the ArangoDB server failed or
        the collection cannot be found.
    """
    if not "database" in config:
        raise ConfigError("Setting missing in config file: 'database'.")
    if connection.hasDatabase(config["database"]):
        return connection[config["database"]]
    elif create:
        return connection.createDatabase(name=config["database"])
    else:
        raise DBError(f"Database '{config['database']}' not found.")


def get_docs(config: Dict, db: Database) -> Collection:
    """
    Access a collection of documents with an ArangoDB database.

    Parameters
    ----------
    config : Dict
        A configuration file containing the database settings,
        including "documentcollection", which holds the name
        of the ArangoDB Collection in which the documents are
        stored.
    db : Database
        An ArangoDB database handle

    Returns
    -------
    Collection
        A collection of documents stored in ArangoDB

    Raises
    ------
    ConfigError
        If the "documentcollection" entry is missing in the config file.
    DBError
        If the connection to the ArangoDB server failed or
        the collection cannot be found.
    """
    if not "documentcollection" in config:
        raise ConfigError("Setting missing in config file: 'documentcollection'.")
    if db.hasCollection(config["documentcollection"]):
        return db[config["documentcollection"]]
    else:
        raise DBError(f"Collection '{config['documentcollection']}' not found.")
