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


def test_zstd_open():
    filename = "tests/data/2007-001.xml.zst"
    mode = "rt"
    encoding = "utf-8"
    with zstd_open(filename, mode, encoding) as data:
        lines = data.readlines()
        assert lines[0] == '<?xml version="1.0" encoding="UTF-8"?>\n'


def test_pdfsave():
    file = "tests/data/bibtex.bib"
    data = pdfsave(file)
    assert data == ""
    file = "tests/data/Jie2019a-Better-Modeling-Incomplete.bib"
    data = pdfsave(file)
    assert data == ""
    file = "tests/data/Jindal2019a-Effective-Label-Noise.bib"
    data = pdfsave(file)
    assert data[:10] == "JVBERi0xLj"  # sehr langer text zeugs


# def test_handleBulkError():
#     # spezialzeugs mach ma später
#     # mit doc_format = "pubmed" muss datenbank inhalt abgefragt werden
#     # ansonsten fehlermeldungen
#     handleBulkError(e, docs, collection, doc_format)

# def test_parallel_import():
#     parallel_import(batch, batch_size, doc_format, open_func, parse, update, pdf)


def test_import_file():
    # eigentliches herzstück
    # greift auf bestehende (leere) arango datenbank zu
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
    for key in ["Jie2019a", "Jie2019b", "Jie2019c"]:
        try:
            doc = collection[key]
        except DocumentNotFoundError:
            assert 1 == 2
        assert doc["cited_by"] == "test"
        assert (
            doc["pdf"] == None
        )  # arangodb gibt bei nicht existierenden attribut None zurück

    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    # gibt loggin.error aus, da daten bereits vorhanden, aber update false

    doc = collection.createDocument()
    doc._key = "Jindal2019a"
    doc["test"] = "test"
    doc.save()
    file = "tests/data/Jindal2019a-Effective-Label-Noise.bib"
    update = True
    pdf = True
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    try:
        doc = collection["Jindal2019a"]
    except DocumentNotFoundError:
        assert 1 == 2
    assert doc["pdf"] != None
    assert doc["test"] == None

    file = "tests/data/Jie2019a-Better-Modeling-Incomplete.bib"
    update = True
    pdf = True
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    try:
        doc = collection["Jie2019a"]
    except DocumentNotFoundError:
        assert 1 == 2
    assert doc["pdf"] == None
    assert doc["test"] == None

    file = "tests/data/bibtex_error.bib.gz"
    compression = "gzip"
    open_func = OPEN_DICT[compression]
    update = True
    pdf = True
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    for key in ["Jie2019a", "Jie2019b", "Jie2019c"]:
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
    for key in ["Jie2019a", "Jie2019b", "Jie2019c"]:
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
        doc = collection["oai:arXiv.org:0704.0004"]
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
        doc = collection["10.5441_002_edbt.2016.69"]
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
        doc = collection["PMID28618900"]
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
        join(".", "tests", "data", "Jie2019a-Better-Modeling-Incomplete.bib"),
        join(".", "tests", "data", "Jindal2019a-Effective-Label-Noise.bib"),
    ]
    control.sort()
    files = locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control
    recursive = True
    control = [
        join(".", "tests", "data", "bibtex.bib"),
        join(".", "tests", "data", "bibtex_error.bib"),
        join(".", "tests", "data", "Jie2019a-Better-Modeling-Incomplete.bib"),
        join(".", "tests", "data", "Jindal2019a-Effective-Label-Noise.bib"),
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
    control = [join(".", "tests", "data", "2007-001.xml.zst")]
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control
    compression = "gzip"
    doc_format = "bibtex"
    control = [join(".", "tests", "data", "bibtex_error.bib.gz")]
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control


# def test_main():
#     main(doc_format, path, pdf, recursive, compression, update, batch_size)

# def test_parallel_main():
#     parallel_main(parallel, cluster, doc_format, path, pdf, recursive, compression, update, batch_size)
