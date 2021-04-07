#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 16:18:45 2019

This module implements commonly used methods like connecting to
an ArangoDB instance.

- connect(Dict): Initial connection to an ArangoDB instance
                 using credentials

@author: tech
"""
from typing import Dict

from pyArango.connection import Connection

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
