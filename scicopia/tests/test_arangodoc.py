from arangodoc import *
from os.path import join


def connection():
    config = read_config()
    if "arango_url" in config:
        arangoconn = Connection(
            arangoURL=config["arango_url"],
            username=config["username"],
            password=config["password"],
        )
    else:
        arangoconn = Connection(
            username=config["username"], password=config["password"]
        )

    if arangoconn.hasDatabase(config["database"]):
        db = arangoconn[config["database"]]
    else:
        db = arangoconn.createDatabase(name=config["database"])
    return db


def test_create_id():
    doc = {"PMID": "12345"}
    doc_format = "pubmed"
    create_id(doc, doc_format)
    assert "id" in doc
    assert doc["id"] == "PMID12345"


def test_zstd_open(): # TODO: make bibtex.bib.zst
    filename = "tests/data/bibtex.bib.zst"
    mode = "rt"
    encoding = "utf-8"
    with zstd_open(filename, mode, encoding) as data:
        lines = data.readlines()
        assert lines[0] == '<?xml version="1.0" encoding="UTF-8"?>\n'


def test_pdfsave():
    file = "tests/data/bibtex.bib"
    data = pdfsave(file)
    assert data == ""
    file = "tests/data/bibtex_error2.bib"
    data = pdfsave(file)
    assert data == ""
    file = "tests/data/bibtex_error.bib"
    data = pdfsave(file)
    assert data[:10] == "TG9yZW0gaX"
    # no guarantee that the file can open
    file = "tests/data/bibtex_pdf.bib"
    data = pdfsave(file)
    assert data[:10] == "JVBERi0xLj"


# def test_handleBulkError():
#     # spezialzeugs mach ma später
#     # mit doc_format = "pubmed" muss datenbank inhalt abgefragt werden
#     # ansonsten fehlermeldungen
#     handleBulkError(e, docs, collection, doc_format)

# def test_parallel_import():
#     parallel_import(batch, batch_size, doc_format, open_func, parse, update, pdf)


def test_import_file():
    db = connection()  # use a config to a test database
    col = "import_file"
    if db.hasCollection(col):
        collection = db[col]
        collection.empty()
    else:
        collection = db.createCollection(name=col)

    batch_size = 2

    file = "tests/data/bibtex.bib"
    doc_format = "bibtex"
    compression = "none"
    open_func = OPEN_DICT[compression]
    parse = PARSE_DICT[doc_format]
    update = False
    pdf = False
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except DocumentNotFoundError:
            assert 1 == 2
        assert doc["cited_by"] == "test"
        assert (
            doc["pdf"] == None
        )  # arangodb returns None if the attribut does not exist

    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    # gibt loggin.error aus, da daten bereits vorhanden, aber update false -> TODO: abfangen

    doc = collection.createDocument()
    doc._key = "PDF"
    doc["test"] = "test"
    doc.save()
    file = "tests/data/bibtex_pdf.bib"
    update = True
    pdf = True
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    try:
        doc = collection["PDF"]
    except DocumentNotFoundError:
        assert 1 == 2
    assert doc["pdf"] != None
    assert doc["test"] == None

    file = "tests/data/bibtex_error.bib"
    update = True
    pdf = True
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    try:
        doc = collection["Ipsum2019a"]
    except DocumentNotFoundError:
        assert 1 == 2
    assert doc["pdf"] == None
    assert doc["test"] == None

    file = "tests/data/bibtex.bib.gz"
    compression = "gzip"
    open_func = OPEN_DICT[compression]
    update = True
    pdf = True
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except DocumentNotFoundError:
            assert 1 == 2
        assert doc["pdf"] == None

    file = "tests/data/bibtex.bib.bz2"
    compression = "bzip2"
    open_func = OPEN_DICT[compression]
    update = True
    pdf = True
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except DocumentNotFoundError:
            assert 1 == 2
        assert doc["cited_by"] == "test"
        assert doc["pdf"] == None

    file = "tests/data/bibtex.bib.zst"
    compression = "bzip2"
    open_func = OPEN_DICT[compression]
    update = True
    pdf = True
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except DocumentNotFoundError:
            assert 1 == 2
        assert doc["cited_by"] == "test"
        assert doc["pdf"] == None

    file = "tests/data/arxiv.xml"
    doc_format = "arxiv"
    compression = "none"
    open_func = OPEN_DICT[compression]
    parse = PARSE_DICT[doc_format]
    update = False
    pdf = False
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    try:
        doc = collection["oai:arXiv.org:121518513"]
    except DocumentNotFoundError:
        assert 1 == 2

    file = "tests/data/grobid.xml"
    doc_format = "grobid"
    compression = "none"
    open_func = OPEN_DICT[compression]
    parse = PARSE_DICT[doc_format]
    update = False
    pdf = False
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    try:
        doc = collection["121518513"]
    except DocumentNotFoundError:
        assert 1 == 2

    file = "tests/data/pubmed.xml"
    doc_format = "pubmed"
    compression = "none"
    open_func = OPEN_DICT[compression]
    parse = PARSE_DICT[doc_format]
    update = False
    pdf = False
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    try:
        doc = collection["PMID121518513"]
    except DocumentNotFoundError:
        assert 1 == 2


def test_import_file_error():
    # tests what happens if the modul is called with wrong combinations
    db = connection()  # use a config to a test database
    col = "import_file_error"
    if db.hasCollection(col):
        collection = db[col]
        collection.empty()
    else:
        collection = db.createCollection(name=col)
    batch_size = 2
    update = False
    pdf = False
    compression = "none"
    open_func = OPEN_DICT[compression]

    # file = "tests/data/bibtex.bib"
    # doc_format = "arxiv"
    # parse = PARSE_DICT[doc_format]
    # import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    # doc_format = "grobid"
    # parse = PARSE_DICT[doc_format]
    # import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    # doc_format = "pubmed"
    # parse = PARSE_DICT[doc_format]
    # import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    file = "tests/data/arxiv.xml"
    # doc_format = "bibtex"
    # parse = PARSE_DICT[doc_format]
    # import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "grobid"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "pubmed"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    file = "tests/data/grobid.xml"
    # doc_format = "bibtex"
    # parse = PARSE_DICT[doc_format]
    # import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "arxiv"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "pubmed"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    file = "tests/data/pubmed.xml"
    # doc_format = "bibtex"
    # parse = PARSE_DICT[doc_format]
    # import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "arxiv"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "grobid"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)


def test_locate_files():
    path = "./tests/data"

    compression = "none"
    doc_format = "bibtex"
    recursive = False
    control = [
        join(".", "tests", "data", "bibtex.bib"),
        join(".", "tests", "data", "bibtex_error.bib"),
        join(".", "tests", "data", "bibtex_pdf.bib"),
    ]
    control.sort()
    files = locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control
    recursive = True
    control = [
        join(".", "tests", "data", "bibtex.bib"),
        join(".", "tests", "data", "bibtex_error.bib"),
        join(".", "tests", "data", "bibtex_pdf.bib"),
        join(".", "tests", "data", "test", "r1.bib"),
        join(".", "tests", "data", "test", "test", "r2.bib"),
    ]
    control.sort()
    files = locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control

    control = [
        join(".", "tests", "data", "arxiv.xml"),
        join(".", "tests", "data", "grobid.xml"),
        join(".", "tests", "data", "grobid_error.xml"),
        join(".", "tests", "data", "grobid_error2.xml"),
        join(".", "tests", "data", "grobid_error3.xml"),
        join(".", "tests", "data", "grobid_error4.xml"),
        join(".", "tests", "data", "grobid_error5.xml"),
        join(".", "tests", "data", "pubmed.xml"),
    ]
    control.sort()
    controlr = [
        join(".", "tests", "data", "arxiv.xml"),
        join(".", "tests", "data", "grobid.xml"),
        join(".", "tests", "data", "grobid_error.xml"),
        join(".", "tests", "data", "grobid_error2.xml"),
        join(".", "tests", "data", "grobid_error3.xml"),
        join(".", "tests", "data", "grobid_error4.xml"),
        join(".", "tests", "data", "grobid_error5.xml"),
        join(".", "tests", "data", "pubmed.xml"),
        join(".", "tests", "data", "test", "grobid.xml"),
        join(".", "tests", "data", "test", "r1.xml"),
        join(".", "tests", "data", "test", "test", "r2.xml"),
    ]
    controlr.sort()

    doc_format = "arxiv"
    recursive = False
    files = locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control
    recursive = True
    files = locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == controlr

    doc_format = "grobid"
    recursive = False
    files = locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control
    recursive = True
    files = locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == controlr

    doc_format = "pubmed"
    recursive = False
    files = locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control
    recursive = True
    files = locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == controlr

    recursive = False
    compression = "zstd"
    doc_format = "pubmed"
    control = [join(".", "tests", "data", "bibtex.bib.zst")]
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control
    compression = "gzip"
    doc_format = "bibtex"
    control = [join(".", "tests", "data", "bibtex.bib.gz")]
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control
    compression = "bzip2"
    doc_format = "bibtex"
    control = [join(".", "tests", "data", "bibtex.bib.bz2")]
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control


# def test_main():
#     main(doc_format, path, pdf, recursive, compression, update, batch_size)

# def test_parallel_main():
#     parallel_main(parallel, cluster, doc_format, path, pdf, recursive, compression, update, batch_size)
