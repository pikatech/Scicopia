import os
import scicopia.arangodoc as arangodoc


def connection():
    config = arangodoc.read_config()
    if "arango_url" in config:
        arangoconn = arangodoc.Connection(
            arangoURL=config["arango_url"],
            username=config["username"],
            password=config["password"],
        )
    else:
        arangoconn = arangodoc.Connection(
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
    arangodoc.create_id(doc, doc_format)
    assert "id" in doc
    assert doc["id"] == "PMID12345"


def test_zstd_open():
    filename = "scicopia/tests/data/bibtex.bib.zst"
    mode = "rt"
    encoding = "utf-8"
    with arangodoc.zstd_open(filename, mode, encoding) as data:
        lines = data.readlines()
        assert lines[0] == "@inproceedings{Ipsum2019a,\n"


def test_pdfsave():
    file = "scicopia/tests/data/bibtex.bib"
    data = arangodoc.pdfsave(file)
    assert data == ""
    file = "scicopia/tests/data/bibtex_error2.bib"
    data = arangodoc.pdfsave(file)
    assert data == ""
    file = "scicopia/tests/data/bibtex_error.bib"
    data = arangodoc.pdfsave(file)
    assert data[:10] == "TG9yZW0gaX"
    # no guarantee that the file can open
    file = "scicopia/tests/data/bibtex_pdf.bib"
    data = arangodoc.pdfsave(file)
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

    file = "scicopia/tests/data/bibtex.bib"
    doc_format = "bibtex"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except arangodoc.DocumentNotFoundError:
            assert 1 == 2
        assert doc["cited_by"] == "test"
        assert (
            doc["pdf"] == None
        )  # arangodb returns None if the attribut does not exist

    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )
    # gibt loggin.error aus, da daten bereits vorhanden, aber update false -> TODO: abfangen

    doc = collection.createDocument()
    doc._key = "PDF"
    doc["test"] = "test"
    doc.save()
    file = "scicopia/tests/data/bibtex_pdf.bib"
    update = True
    pdf = True
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )
    try:
        doc = collection["PDF"]
    except arangodoc.DocumentNotFoundError:
        assert 1 == 2
    assert doc["pdf"] != None
    assert doc["test"] == None

    file = "scicopia/tests/data/bibtex_error.bib"
    update = True
    pdf = True
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )
    try:
        doc = collection["Ipsum2019a"]
    except arangodoc.DocumentNotFoundError:
        assert 1 == 2
    assert doc["pdf"] == None
    assert doc["test"] == None

    file = "scicopia/tests/data/bibtex.bib.gz"
    compression = "gzip"
    open_func = arangodoc.OPEN_DICT[compression]
    update = True
    pdf = True
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except arangodoc.DocumentNotFoundError:
            assert 1 == 2
        assert doc["pdf"] == None

    file = "scicopia/tests/data/bibtex.bib.bz2"
    compression = "bzip2"
    open_func = arangodoc.OPEN_DICT[compression]
    update = True
    pdf = True
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except arangodoc.DocumentNotFoundError:
            assert 1 == 2
        assert doc["cited_by"] == "test"
        assert doc["pdf"] == None

    file = "scicopia/tests/data/bibtex.bib.zst"
    compression = "zstd"
    open_func = arangodoc.OPEN_DICT[compression]
    update = True
    pdf = True
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except arangodoc.DocumentNotFoundError:
            assert 1 == 2
        assert doc["cited_by"] == "test"
        assert doc["pdf"] == None

    file = "scicopia/tests/data/arxiv.xml"
    doc_format = "arxiv"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )
    try:
        doc = collection["oai:arXiv.org:121518513"]
    except arangodoc.DocumentNotFoundError:
        assert 1 == 2

    file = "scicopia/tests/data/grobid.xml"
    doc_format = "grobid"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )
    try:
        doc = collection["121518513"]
    except arangodoc.DocumentNotFoundError:
        assert 1 == 2

    file = "scicopia/tests/data/pubmed.xml"
    doc_format = "pubmed"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )
    try:
        doc = collection["PMID121518513"]
    except arangodoc.DocumentNotFoundError:
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
    open_func = arangodoc.OPEN_DICT[compression]

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

    file = "scicopia/tests/data/arxiv.xml"
    # doc_format = "bibtex"
    # parse = PARSE_DICT[doc_format]
    # import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "grobid"
    parse = arangodoc.PARSE_DICT[doc_format]
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )

    doc_format = "pubmed"
    parse = arangodoc.PARSE_DICT[doc_format]
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )

    file = "scicopia/tests/data/grobid.xml"
    # doc_format = "bibtex"
    # parse = PARSE_DICT[doc_format]
    # import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "arxiv"
    parse = arangodoc.PARSE_DICT[doc_format]
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )

    doc_format = "pubmed"
    parse = arangodoc.PARSE_DICT[doc_format]
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )

    file = "scicopia/tests/data/pubmed.xml"
    # doc_format = "bibtex"
    # parse = PARSE_DICT[doc_format]
    # import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "arxiv"
    parse = arangodoc.PARSE_DICT[doc_format]
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )

    doc_format = "grobid"
    parse = arangodoc.PARSE_DICT[doc_format]
    arangodoc.import_file(
        file, collection, batch_size, doc_format, open_func, parse, update, pdf
    )


def test_locate_bibtex_nonrecursive():
    path = "./scicopia/tests/data"

    compression = "none"
    doc_format = "bibtex"
    recursive = False
    control = [
        f"{path}{os.path.sep}bibtex.bib",
        f"{path}{os.path.sep}bibtex_error.bib",
        f"{path}{os.path.sep}bibtex_error2.bib",
        f"{path}{os.path.sep}bibtex_pdf.bib",
    ]
    control.sort()
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control
    recursive = True


def test_locate_bibtex_recursive():
    path = "./scicopia/tests/data"

    compression = "none"
    doc_format = "bibtex"
    recursive = True
    control = [
        f"{path}{os.path.sep}bibtex.bib",
        f"{path}{os.path.sep}bibtex_error.bib",
        f"{path}{os.path.sep}bibtex_error2.bib",
        f"{path}{os.path.sep}bibtex_pdf.bib",
        f"{path}{os.path.sep}test{os.path.sep}r1.bib",
        f"{path}{os.path.sep}test{os.path.sep}test{os.path.sep}r2.bib",
    ]
    control.sort()
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control


def test_locate_arxiv_nonrecursive():
    path = "./scicopia/tests/data"

    compression = "none"
    doc_format = "arxiv"
    recursive = False
    control = [
        f"{path}{os.path.sep}arxiv.xml",
        f"{path}{os.path.sep}grobid.xml",
        f"{path}{os.path.sep}grobid_error.xml",
        f"{path}{os.path.sep}grobid_error2.xml",
        f"{path}{os.path.sep}grobid_error3.xml",
        f"{path}{os.path.sep}grobid_error4.xml",
        f"{path}{os.path.sep}grobid_error5.xml",
        f"{path}{os.path.sep}grobid_error6.xml",
        f"{path}{os.path.sep}grobid_error7.xml",
        f"{path}{os.path.sep}pubmed.xml",
    ]
    control.sort()
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control


def test_locate_arxiv_recursive():
    path = "./scicopia/tests/data"

    compression = "none"
    doc_format = "arxiv"
    recursive = True
    control = [
        f"{path}{os.path.sep}arxiv.xml",
        f"{path}{os.path.sep}grobid.xml",
        f"{path}{os.path.sep}grobid_error.xml",
        f"{path}{os.path.sep}grobid_error2.xml",
        f"{path}{os.path.sep}grobid_error3.xml",
        f"{path}{os.path.sep}grobid_error4.xml",
        f"{path}{os.path.sep}grobid_error5.xml",
        f"{path}{os.path.sep}grobid_error6.xml",
        f"{path}{os.path.sep}grobid_error7.xml",
        f"{path}{os.path.sep}pubmed.xml",
        f"{path}{os.path.sep}test{os.path.sep}grobid.xml",
        f"{path}{os.path.sep}test{os.path.sep}r1.xml",
        f"{path}{os.path.sep}test{os.path.sep}test{os.path.sep}r2.xml",
    ]
    control.sort()
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control


def test_locate_grobid_nonrecursive():
    path = "./scicopia/tests/data"

    compression = "none"
    doc_format = "grobid"
    recursive = False
    control = [
        f"{path}{os.path.sep}arxiv.xml",
        f"{path}{os.path.sep}grobid.xml",
        f"{path}{os.path.sep}grobid_error.xml",
        f"{path}{os.path.sep}grobid_error2.xml",
        f"{path}{os.path.sep}grobid_error3.xml",
        f"{path}{os.path.sep}grobid_error4.xml",
        f"{path}{os.path.sep}grobid_error5.xml",
        f"{path}{os.path.sep}grobid_error6.xml",
        f"{path}{os.path.sep}grobid_error7.xml",
        f"{path}{os.path.sep}pubmed.xml",
    ]
    control.sort()
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control


def test_locate_grobid_recursive():
    path = "./scicopia/tests/data"

    compression = "none"
    doc_format = "grobid"
    recursive = True
    control = [
        f"{path}{os.path.sep}arxiv.xml",
        f"{path}{os.path.sep}grobid.xml",
        f"{path}{os.path.sep}grobid_error.xml",
        f"{path}{os.path.sep}grobid_error2.xml",
        f"{path}{os.path.sep}grobid_error3.xml",
        f"{path}{os.path.sep}grobid_error4.xml",
        f"{path}{os.path.sep}grobid_error5.xml",
        f"{path}{os.path.sep}grobid_error6.xml",
        f"{path}{os.path.sep}grobid_error7.xml",
        f"{path}{os.path.sep}pubmed.xml",
        f"{path}{os.path.sep}test{os.path.sep}grobid.xml",
        f"{path}{os.path.sep}test{os.path.sep}r1.xml",
        f"{path}{os.path.sep}test{os.path.sep}test{os.path.sep}r2.xml",
    ]
    control.sort()
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control


def test_locate_pubmed_nonrecursive():
    path = "./scicopia/tests/data"

    compression = "none"
    doc_format = "pubmed"
    recursive = False
    control = [
        f"{path}{os.path.sep}arxiv.xml",
        f"{path}{os.path.sep}grobid.xml",
        f"{path}{os.path.sep}grobid_error.xml",
        f"{path}{os.path.sep}grobid_error2.xml",
        f"{path}{os.path.sep}grobid_error3.xml",
        f"{path}{os.path.sep}grobid_error4.xml",
        f"{path}{os.path.sep}grobid_error5.xml",
        f"{path}{os.path.sep}grobid_error6.xml",
        f"{path}{os.path.sep}grobid_error7.xml",
        f"{path}{os.path.sep}pubmed.xml",
    ]
    control.sort()
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control


def test_locate_pubmed_recursive():
    path = "./scicopia/tests/data"

    compression = "none"
    doc_format = "pubmed"
    recursive = True
    control = [
        f"{path}{os.path.sep}arxiv.xml",
        f"{path}{os.path.sep}grobid.xml",
        f"{path}{os.path.sep}grobid_error.xml",
        f"{path}{os.path.sep}grobid_error2.xml",
        f"{path}{os.path.sep}grobid_error3.xml",
        f"{path}{os.path.sep}grobid_error4.xml",
        f"{path}{os.path.sep}grobid_error5.xml",
        f"{path}{os.path.sep}grobid_error6.xml",
        f"{path}{os.path.sep}grobid_error7.xml",
        f"{path}{os.path.sep}pubmed.xml",
        f"{path}{os.path.sep}test{os.path.sep}grobid.xml",
        f"{path}{os.path.sep}test{os.path.sep}r1.xml",
        f"{path}{os.path.sep}test{os.path.sep}test{os.path.sep}r2.xml",
    ]
    control.sort()
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    files.sort()
    assert files == control


def test_locate_zstd_bibtex():
    path = "./scicopia/tests/data"

    recursive = False
    compression = "zstd"
    doc_format = "bibtex"
    control = [f"{path}{os.path.sep}bibtex.bib.zst"]
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    assert files == control


def test_locate_gzip_bibtex():
    path = "./scicopia/tests/data"

    recursive = False
    compression = "gzip"
    doc_format = "bibtex"
    control = [f"{path}{os.path.sep}bibtex.bib.gz"]
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    assert files == control


def test_locate_bzip2_bibtex():
    path = "./scicopia/tests/data"

    recursive = False
    compression = "bzip2"
    doc_format = "bibtex"
    control = [f"{path}{os.path.sep}bibtex.bib.bz2"]
    files = arangodoc.locate_files(path, doc_format, recursive, compression)
    assert files == control


# def test_main():
#     main(doc_format, path, pdf, recursive, compression, update, batch_size)

# def test_parallel_main():
#     parallel_main(parallel, cluster, doc_format, path, pdf, recursive, compression, update, batch_size)
