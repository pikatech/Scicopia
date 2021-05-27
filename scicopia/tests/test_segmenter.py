from collections import Counter
import pytest

from scicopia.app.parser.segmenter import QuerySplitter

@pytest.fixture
def splitter():
    counter = Counter({'new york': 13, 'times square': 24, 'square dance': 5, 'new york times': 8})
    query_splitter = QuerySplitter(counter)
    return query_splitter


def test_scoring(splitter):
    query = "new york times square dance".split()
    segments = splitter.segment_query(query)
    assert segments == [['new', 'york', 'times'], ['square', 'dance']]