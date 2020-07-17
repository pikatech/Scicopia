from scicopia.parsers.grobid import *


def test_remove_refs():
    source = "scicopia/tests/data/grobid.xml"
    with open(source, encoding="utf-8") as filename:
        xml = filename.read()
        xml = xml.replace(" <ref", "<ref")
        root = ET.fromstring(xml)
        del xml

        remove_refs(root)


def test_extract_title():
    source = [
        "scicopia/tests/data/grobid.xml",
        "scicopia/tests/data/grobid_error.xml",
        "scicopia/tests/data/grobid_error2.xml",
    ]
    for file in source:
        with open(file, encoding="utf-8") as filename:
            xml = filename.read()
            xml = xml.replace(" <ref", "<ref")
            root = ET.fromstring(xml)
            del xml

            remove_refs(root)
            node = root.find(f"{TEI}teiHeader/{FILEDESC}")
            data = dict()
            title = node.find(f"{TEI}titleStmt")
            if not title is None:
                extract_title(title, data)
                if "title" in data:
                    assert (
                        data["title"]
                        == "Lorem ipsum dolor"
                    )


def test_extract_authors():
    source = ["scicopia/tests/data/grobid.xml", "scicopia/tests/data/grobid_error.xml"]
    for file in source:
        with open(file, encoding="utf-8") as filename:
            xml = filename.read()
            xml = xml.replace(" <ref", "<ref")
            root = ET.fromstring(xml)
            del xml

            remove_refs(root)
            node = root.find(f"{TEI}teiHeader/{FILEDESC}")
            data = dict()

            structured_info = node.find(f"{TEI}sourceDesc/{TEI}biblStruct")
            if not structured_info is None:
                authors = structured_info.findall(f"{TEI}analytic/{TEI}author")
                if authors:
                    extract_authors(authors, data)
                    if "author" in data:
                        assert data["author"] == [
                            "Lorem Ipsum",
                            "Lörem Ipßüm"
                        ]


def test_extract_bibliographic_data():
    source = [
        "scicopia/tests/data/grobid.xml",
        "scicopia/tests/data/grobid_error.xml",
        "scicopia/tests/data/grobid_error2.xml",
        "scicopia/tests/data/grobid_error3.xml",
        "scicopia/tests/data/grobid_error4.xml",
        "scicopia/tests/data/grobid_error5.xml",
    ]
    for file in source:
        with open(file, encoding="utf-8") as filename:
            xml = filename.read()
            xml = xml.replace(" <ref", "<ref")
            root = ET.fromstring(xml)
            del xml

            remove_refs(root)
            biblio = root.find(f"{TEI}teiHeader/{FILEDESC}")
            if biblio is not None and biblio.text is not None:
                bib = extract_bibliographic_data(biblio)

                if "author" in bib:
                    assert bib["author"] == [
                        "Lorem Ipsum",
                        "Lörem Ipßüm"
                    ]
                if "title" in bib:
                    assert (
                        bib["title"]
                        == "Lorem ipsum dolor"
                    )
                if "doi" in bib:
                    assert bib["doi"] == "121518513"
                if "url" in bib:
                    assert (
                        bib["url"] == "https://arxiv.org/abs/121518513"
                    )
                if "id" in bib:
                    assert (
                        bib["id"] == "121518513"
                        or bib["id"] == "abs/121518513"
                    )
                if "date" in bib:
                    assert bib["date"] == "2020" or bib["date"] == "2020-02-02"
                if "year" in bib:
                    assert bib["year"] == "2020"


def test_extract_text():
    source = [
        "scicopia/tests/data/grobid.xml",
        "scicopia/tests/data/grobid_error.xml",
        "scicopia/tests/data/grobid_error2.xml",
    ]
    for file in source:
        with open(file, encoding="utf-8") as filename:
            xml = filename.read()
            xml = xml.replace(" <ref", "<ref")
            root = ET.fromstring(xml)
            del xml

            remove_refs(root)
            text = extract_text(root)

            assert (
                text
                == "ABSTRACT\nLorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\nINTRODUCTION\nLorem ipsum."
            )


def test_parse():
    source = [
        "scicopia/tests/data/grobid.xml",
        "scicopia/tests/data/grobid_error.xml",
        "scicopia/tests/data/grobid_error2.xml",
    ]
    for file in source:
        with open(file, encoding="utf-8") as filename:
            for bib in parse(filename):
                if "author" in bib:
                    assert bib["author"] == [
                        "Lorem Ipsum",
                        "Lörem Ipßüm"
                    ]
                if "title" in bib:
                    assert (
                        bib["title"]
                        == "Lorem ipsum dolor"
                    )
                if "doi" in bib:
                    assert bib["doi"] == "121518513"
                if "id" in bib:
                    assert (
                        bib["id"] == "121518513"
                        or bib["id"] == "abs/121518513"
                    )
                if "fulltext" in bib:
                    assert (
                        bib["fulltext"]
                        == "ABSTRACT\nLorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\nINTRODUCTION\nLorem ipsum."
                    )
