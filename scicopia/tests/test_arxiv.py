from parsers.arxiv import *


def test_parse():
    source = "tests/data/arxiv.xml"
    with open(source) as data:
        for datadict in parse(data):
            assert "id" in datadict
            assert datadict["id"] == "oai:arXiv.org:121518513"
            assert "date" in datadict
            assert datadict["date"] == "2007-05-23" or datadict["date"] == "05/23/2007"
            if "year" in datadict:
                assert datadict["year"] == "2007"
            assert "setSpec" in datadict
            assert datadict["setSpec"] == {"lor"} or datadict["setSpec"] == set()
            assert "title" in datadict
            assert (
                datadict["title"]
                == "Lorem ipsum   dolor"
            )
            assert "author" in datadict
            assert datadict["author"] == ("Ipsum, Lorem",)
            assert "subject" in datadict
            assert datadict["subject"] == {"12O18", "Lorem - Ipsum"}
            assert "abstract" in datadict
            assert (
                datadict["abstract"]
                == "Lorem ipsum dolor sit amet, consetetur sadipscing elitr. \nComment: 11 pages"
            )
            if "meta_id" in datadict:
                assert datadict["meta_id"] == ("http://arxiv.org/abs/121518513",)
