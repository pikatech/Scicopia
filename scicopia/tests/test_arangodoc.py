#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 13:51:04 2020

@author: tech
"""

from arangodoc import locate_files

def test_locate_files():
    path = "tests/data/import"
    doc_format = "arxiv"
    recursive = True
    compression = "zstd"
    files = locate_files(path, doc_format, recursive, compression)

    assert len(files) == 2
