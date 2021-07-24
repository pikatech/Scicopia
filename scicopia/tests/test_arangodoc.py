import os

import scicopia.arangodoc as arangodoc
from scicopia.utils.arangodb import connect, select_db



def connection(col):
    # use a config to a test database
    config = arangodoc.read_config()
    arangoconn = connect(config)
    db = select_db(config, arangoconn, create=True)
    if db.hasCollection(col):
        collection = db[col]
        collection.empty()
    else:
        collection = db.createCollection(name=col)
    pdfcol = "import_pdf"
    if db.hasCollection(pdfcol):
        pdfcollection = db[pdfcol]
        pdfcollection.empty()
    else:
        pdfcollection = db.createCollection(name=pdfcol)

    batch_size = 2
    return collection, pdfcollection, batch_size


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
    # no guarantee that the file can open
    file = "scicopia/tests/data/bibtex_pdf.bib"
    data = arangodoc.pdfsave(file)
    assert data[:10] == "B~V00Eio=N"

def test_pdfsave_noPDF():
    file = "scicopia/tests/data/bibtex.bib"
    data = arangodoc.pdfsave(file)
    assert data == ""

def test_pdfsave_damagedPDF():
    file = "scicopia/tests/data/bibtex_error.bib"
    data = arangodoc.pdfsave(file)
    assert data[:10] == "OmA{!Z6IlI"

def test_pdfsave_emptyPDF():
    file = "scicopia/tests/data/bibtex_error2.bib"
    data = arangodoc.pdfsave(file)
    assert data == ""


# def test_handleBulkError():
#     # spezialzeugs mach ma später
#     # mit doc_format = "pubmed" muss datenbank inhalt abgefragt werden
#     # ansonsten fehlermeldungen
#     handleBulkError(e, docs, collection, doc_format)

# def test_parallel_import():
#     parallel_import(batch, batch_size, doc_format, open_func, parse, update, pdf)

def test_import_file_bibtex():
    collection, pdfcollection, batch_size = connection("import_file")
    file = "scicopia/tests/data/bibtex.bib"
    doc_format = "bibtex"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        assert key in collection
        assert collection[key]["cited_by"] == "test"
        assert not key in pdfcollection

def test_import_file_arxiv():
    collection, pdfcollection, batch_size = connection("import_file")
    file = "scicopia/tests/data/arxiv.xml"
    doc_format = "arxiv"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    assert "oai:arXiv.org:121518513" in collection

def test_import_file_grobid():
    collection, pdfcollection, batch_size = connection("import_file")
    file = "scicopia/tests/data/grobid.xml"
    doc_format = "grobid"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    assert "121518513" in collection

def test_import_file_pubmed():
    collection, pdfcollection, batch_size = connection("import_file")
    file = "scicopia/tests/data/pubmed.xml"
    doc_format = "pubmed"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    assert "PMID121518513" in collection

def test_import_file_update_pdf():
    collection, pdfcollection, batch_size = connection("import_file")
    doc = collection.createDocument()
    doc._key = "PDF"
    doc["test"] = "test"
    doc.save()
    file = "scicopia/tests/data/bibtex_pdf.bib"
    doc_format = "bibtex"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = True
    pdf = True
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    assert "PDF" in collection
    assert collection["PDF"]["test"] is None
    assert "PDF" in pdfcollection
    # TODO: chatch and assert loggin.error

def test_import_file_update_noPDF():
    collection, pdfcollection, batch_size = connection("import_file")
    file = "scicopia/tests/data/bibtex.bib"
    doc_format = "bibtex"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = True
    pdf = True
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    assert "Ipsum2019a" in collection
    assert collection["Ipsum2019a"]["test"] == None
    assert not "Ipsum2019a" in pdfcollection
    # TODO: chatch and assert loggin.error
    
def test_import_file_update_error():
    collection, pdfcollection, batch_size = connection("import_file")
    file = "scicopia/tests/data/bibtex.bib"
    doc_format = "bibtex"
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    parse = arangodoc.PARSE_DICT[doc_format]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )    
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    # TODO: chatch and assert loggin.error

def test_import_file_gz():
    collection, pdfcollection, batch_size = connection("import_file")
    file = "scicopia/tests/data/bibtex.bib.gz"
    doc_format = "bibtex"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "gzip"
    open_func = arangodoc.OPEN_DICT[compression]
    update = True
    pdf = True
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except arangodoc.DocumentNotFoundError:
            assert False
        try:
            doc = pdfcollection[key]
            assert False
        except arangodoc.DocumentNotFoundError:
            pass

def test_import_file_bz2():
    collection, pdfcollection, batch_size = connection("import_file")
    file = "scicopia/tests/data/bibtex.bib.bz2"
    doc_format = "bibtex"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "bzip2"
    open_func = arangodoc.OPEN_DICT[compression]
    update = True
    pdf = True
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except arangodoc.DocumentNotFoundError:
            assert False
        assert doc["cited_by"] == "test"
        try:
            doc = pdfcollection[key]
            assert False
        except arangodoc.DocumentNotFoundError:
            pass

def test_import_file_zst():
    collection, pdfcollection, batch_size = connection("import_file")
    file = "scicopia/tests/data/bibtex.bib.zst"
    doc_format = "bibtex"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "zstd"
    open_func = arangodoc.OPEN_DICT[compression]
    update = True
    pdf = True
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )
    for key in ["Ipsum2019a", "Ipsum2019b", "Ipsum2019c"]:
        try:
            doc = collection[key]
        except arangodoc.DocumentNotFoundError:
            assert False
        assert doc["cited_by"] == "test"
        try:
            doc = pdfcollection[key]
            assert False
        except arangodoc.DocumentNotFoundError:
            pass


# tests what happens if the modul is called with wrong combinations
def test_import_file_error_bibtex_arxiv():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/bibtex.bib"
    doc_format = "arxiv"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_bibtex_grobid():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/bibtex.bib"
    doc_format = "grobid"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_bibtex_pubmed():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/bibtex.bib"
    doc_format = "pubmed"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_arxiv_bibtex():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/arxiv.xml"
    doc_format = "bibtex"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_arxiv_grobid():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/arxiv.xml"
    doc_format = "grobid"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_arxiv_pubmed():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/arxiv.xml"
    doc_format = "pubmed"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_grobid_bibtex():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/grobid.xml"
    doc_format = "bibtex"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_grobid_arxiv():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/grobid.xml"
    doc_format = "arxiv"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_grobid_pubmed():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/grobid.xml"
    doc_format = "pubmed"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_pubmed_bibtex():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/pubmed.xml"
    doc_format = "bibtex"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_pubmed_arxiv():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/pubmed.xml"
    doc_format = "arxiv"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
    )

def test_import_file_error_pubmed_grobid():
    collection, pdfcollection, batch_size = connection("import_file_error")
    pdfcollection = None
    file = "scicopia/tests/data/pubmed.xml"
    doc_format = "grobid"
    parse = arangodoc.PARSE_DICT[doc_format]
    compression = "none"
    open_func = arangodoc.OPEN_DICT[compression]
    update = False
    pdf = False
    arangodoc.import_file(
        file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
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
