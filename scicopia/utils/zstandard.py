#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 15:28:35 2021

@author: tech
"""

import pickle
from contextlib import contextmanager
from io import TextIOWrapper
from typing import Any, Iterator, TextIO

import zstandard as zstd


def zstd_unpickle(filename: str) -> Any:
    """
    Unpickles a Zstandard-compressed object.

    Parameters
    ----------
    filename : str
        The path to the storage destination of the file

    Returns
    -------
    Any
        Any picklable object
    """
    dctx = zstd.ZstdDecompressor()
    with open(filename, mode="rb") as fh:
        with dctx.stream_reader(fh) as reader:
            obj = pickle.load(reader)
    return obj


@contextmanager
def zstd_open(
    filename: str, mode: str = "rb", encoding: str = "utf-8"
) -> Iterator[TextIO]:
    """
    This is an auxilliary function to provide an open() function which supports
    readline(), as ZstdDecompressor and the object produced by
    ZstdDecompressor.stream_reader() don't have one.'

    Parameters
    ----------
    filename : str
        The path to the storage destination of the file
    mode : str, optional
        This parameter only exists to keep compatibility with other open()
        functions and will be ignored. Interally, the mode is always 'rb'.
        The default is 'rb'.
    encoding : str, optional
        The name of the encoding used in the file. The default is 'utf-8'.

    Yields
    ------
    TextIOWrapper
        A buffered text stream which supports readline()

    """
    dctx = zstd.ZstdDecompressor()
    with open(filename, mode="rb") as fh:
        with dctx.stream_reader(fh) as reader:
            yield TextIOWrapper(reader, encoding=encoding)
