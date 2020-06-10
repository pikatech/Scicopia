#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 16:39:17 2020

@author: tech
"""

import os

from scicopia.app import create_app
from scicopia.app.db import link

def test_link():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    input = ["http://www.example.com/foo links to https://www.example.com/bar"]
    expected = ["<a href=\"http://www.example.com/foo\">http://www.example.com/foo</a> links to <a href=\"https://www.example.com/bar\">https://www.example.com/bar</a>"]
    with app.app_context():
        output = link(input)
    assert output == expected