from parsers.arxiv import *


def test_parse():
    source = "tests/data/arxiv.xml"
    with open(source) as data:
        for datadict in parse(data):
            assert "id" in datadict
            assert datadict["id"] == "oai:arXiv.org:0704.0004"
            assert "date" in datadict
            assert datadict["date"] == "2007-05-23" or datadict["date"] == "05/23/2007"
            if "year" in datadict:
                assert datadict["year"] == "2007"
            assert "setSpec" in datadict
            assert datadict["setSpec"] == {"math"} or datadict["setSpec"] == set()
            assert "title" in datadict
            assert (
                datadict["title"]
                == "A determinant of Stirling cycle numbers counts unlabeled acyclic   single-source automata"
            )
            assert "author" in datadict
            assert datadict["author"] == ("Callan, David",)
            assert "subject" in datadict
            assert datadict["subject"] == {"05A15", "Mathematics - Combinatorics"}
            assert "abstract" in datadict
            assert (
                datadict["abstract"]
                == "We show that a determinant of Stirling cycle numbers counts unlabeled acyclic single-source automata. The proof involves a bijection from these automata to certain marked lattice paths and a sign-reversing involution to evaluate the determinant. \nComment: 11 pages"
            )
            if "meta_id" in datadict:
                assert datadict["meta_id"] == ("http://arxiv.org/abs/0704.0004",)
