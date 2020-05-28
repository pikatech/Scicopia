from io import TextIOWrapper
from contextlib import contextmanager
from typing import Callable, Dict, Generator, List
import zstandard as zstd

filename = "2007-001.xml.zstd"

@contextmanager
def zstd_open(
    filename: str, mode: str = "rb", encoding: str = "utf-8"
) -> Generator[TextIOWrapper, None, None]:
    dctx = zstd.ZstdDecompressor()
    with open(filename, mode="rb") as fh:
        with dctx.stream_reader(fh) as reader:
            yield TextIOWrapper(reader, encoding=encoding)


with zstd_open(filename, "rt", encoding="utf-8") as data:
    data=data.read()
    with open("arxiv.xml", "wt", encoding="utf-8") as out:
        out.write(data)