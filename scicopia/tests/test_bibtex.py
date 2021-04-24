from scicopia.parsers.bibtex import (
    Parser,
    handleField,
    handlePerson,
    parse,
    tex2text,
)


def test_handleField():
    source = "scicopia/tests/data/bibtex.bib"
    parser = Parser()
    bib_data = parser.parse_file(source)
    for entry in bib_data.entries.values():
        fields = list(entry.fields.items())

        datadict = dict()
        handleField(fields[0], datadict)
        assert "year" in datadict
        assert datadict["year"] == "2019"
        handleField(fields[1], datadict)
        assert "publisher" in datadict
        assert datadict["publisher"] == "Association for Lorem Ipsum"
        handleField(fields[2], datadict)
        assert "cited_by" in datadict
        assert datadict["cited_by"] == "test"


def test_handlePerson():
    source = "scicopia/tests/data/bibtex.bib"
    parser = Parser()
    bib_data = parser.parse_file(source)
    for entry in bib_data.entries.values():
        items = list(entry.persons.items())

        datadict = dict()
        handlePerson(items[0], datadict)
        assert "author" in datadict
        assert datadict["author"] == ["Lorem Ipsum", "Lörem Ipßüm"]


def test_parse():
    source = "scicopia/tests/data/bibtex.bib"
    with open(source, encoding="utf-8") as data:
        for datadict in parse(data):
            assert "year" in datadict
            assert datadict["year"] == "2019"
            assert "publisher" in datadict
            assert datadict["publisher"] == "Association for Lorem Ipsum"
            assert "cited_by" in datadict
            assert datadict["cited_by"] == "test"
            assert "author" in datadict
            assert datadict["author"] == ["Lorem Ipsum", "Lörem Ipßüm"]


def test_parse_error():  # TODO: add control of exceptions
    source = "scicopia/tests/data/bibtex_error.bib"
    with open(source, encoding="utf-8") as data:
        for datadict in parse(data):
            pass
    # with open(source) as data:
    #     try:
    #         for datadict in parse(data):
    #             pass
    #     except SystemError as e:
    #         assert e.args == (1,)


def test_tex2text_author():
    bib = {"author": [r"{\AA} \c{C}\"o\u{g}\v{s}\'i"]}
    expected = {"author": ["Å Çöğší"]}
    tex2text(bib)
    assert bib == expected


def test_tex2text_title():
    bib = {"title": r"\textgreater{}Test\textless"}
    expected = {"title": ">Test<"}
    tex2text(bib)
    assert bib == expected


def test_tex2text_emphasis():
    bib = {"title": r"A \emph{Strong} text"}
    expected = {"title": "A <i>Strong</i> text"}
    tex2text(bib)
    assert bib == expected


def test_tex2text_bold():
    bib = {"title": r"A \textbf{Strong} text"}
    expected = {"title": "A <b>Strong</b> text"}
    tex2text(bib)
    assert bib == expected
