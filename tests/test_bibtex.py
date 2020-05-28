import pytest
from scicopia.parsers.bibtex import *

def test_handleField():
    source = "tests/data/bibtex.bib"
    parser = Parser()
    bib_data = parser.parse_file(source)
    for entry in bib_data.entries.itervalues():
        fields = entry.fields.items()

        datadict = dict()
        handleField(fields[0], datadict)
        assert "year" in datadict
        assert datadict["year"]=="2019"
        handleField(fields[1], datadict)
        assert "publisher" in datadict
        assert datadict["publisher"]=="Association for Computational Linguistics"
        handleField(fields[2], datadict)
        assert "cited_by" in datadict
        assert datadict["cited_by"]=="test"

def test_handlePerson():
    source = "tests/data/bibtex.bib"
    parser = Parser()
    bib_data = parser.parse_file(source)
    for entry in bib_data.entries.itervalues():
        items = entry.persons.items()

        datadict = dict()
        handlePerson(items[0], datadict)
        assert "author" in datadict
        assert datadict["author"]== ["Zhanming Jie", "Pengjun Xie", "Wei Lu", "Ruixue Ding", "Linlin Li"]

def test_parse():
    source = "tests/data/bibtex.bib"
    with open(source) as data:
        for datadict in parse(data):
            assert "year" in datadict
            assert datadict["year"]=="2019"
            assert "publisher" in datadict
            assert datadict["publisher"]=="Association for Computational Linguistics"
            assert "cited_by" in datadict
            assert datadict["cited_by"]=="test"
            assert "author" in datadict
            assert datadict["author"]== ["Zhanming Jie", "Pengjun Xie", "Wei Lu", "Ruixue Ding", "Linlin Li"]

            
def test_parse_error(): # TODO: add controll of exceptions
    source = "tests/data/bibtex_error.bib"
    with open(source) as data:
        for datadict in parse(data):
            pass
    # with open(source) as data:
    #     try:
    #         for datadict in parse(data):
    #             pass
    #     except SystemError as e:
    #         assert e.args == (1,)
