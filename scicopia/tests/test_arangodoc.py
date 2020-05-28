from arangodoc import *
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
    filename = "tests/data/2007-001.xml.zstd"
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
    assert data[:10] == "JVBERi0xLj" # sehr langer text zeugs

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
    db = connection()    # use a config to a test database
    col="import_file"
    if db.hasCollection(col):
        db[col].delete()
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
        assert doc["cited_by"]=="test"
        #assert "pdf" in doc #doc["pdf"]=="" # sollte fehler geben, da pdf fehlt
        
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    # gibt loggin.error aus, da daten bereits vorhanden, aber update false

    doc = collection.createDocument()
    doc._key = "Jindal2019a"
    doc["test"] = "test"
    doc.save()
    file = "tests/data/Jindal2019a-Effective-Label-Noise"
    update = True
    pdf = True
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
    try:
        doc = collection["Jindal2019a"]
    except DocumentNotFoundError:
        assert 1 == 2
    assert doc["cited_by"]=="test"
    assert doc["pdf"]!=None
   # assert "test" in doc #doc["test"]=="" # sollte fehler geben, da test fehlt
    
    file = "tests/data/bibtex.bib.gz"
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
        assert doc["cited_by"]=="test"
        #assert "pdf" in doc #doc["pdf"]=="" # sollte fehler geben, da pdf fehlt
    
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
        assert doc["cited_by"]=="test"
        #assert "pdf" in doc #doc["pdf"]=="" # sollte fehler geben, da pdf fehlt

        
    
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
        doc = collection["10.5441/002/edbt.2016.69"]
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
    db = connection()    # use a config to a test database
    col="import_file_error"
    if db.hasCollection(col):
        db[col].delete()
    collection = db.createCollection(name=col)
    batch_size = 2
    update = False
    pdf = False
    compression = "none"
    open_func = OPEN_DICT[compression]

    
    file = "tests/data/bibtex.bib"
    doc_format = "arxiv"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "grobid"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "pubmed"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    file = "tests/data/arxiv.xml"
    doc_format = "bibtex"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "grobid"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "pubmed"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    file = "tests/data/grobid.xml"
    doc_format = "bibtex"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "arxiv"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    doc_format = "pubmed"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

    file = "tests/data/pubmed.xml"
    doc_format = "bibtex"
    parse = PARSE_DICT[doc_format]
    import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)

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
    control = ["./tests/data\\bibtex.bib", "./tests/data\\bibtex_error.bib", "./tests/data\\Jie2019a-Better-Modeling-Incomplete.bib", "./tests/data\\Jindal2019a-Effective-Label-Noise.bib"]
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control
    recursive = True
    control = ["./tests/data\\bibtex.bib", "./tests/data\\bibtex_error.bib", "./tests/data\\Jie2019a-Better-Modeling-Incomplete.bib", "./tests/data\\Jindal2019a-Effective-Label-Noise.bib", "./tests/data\\test\\r1.bib", "./tests/data\\test\\test\\r2.bib"]
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control
    
    control = ["./tests/data\\arxiv.xml", "./tests/data\\grobid.xml", "./tests/data\\grobid_error.xml", "./tests/data\\grobid_error2.xml", "./tests/data\\grobid_error3.xml", "./tests/data\\grobid_error4.xml", "./tests/data\\grobid_error5.xml", "./tests/data\\pubmed.xml"]
    controlr = ["./tests/data\\arxiv.xml", "./tests/data\\grobid.xml", "./tests/data\\grobid_error.xml", "./tests/data\\grobid_error2.xml", "./tests/data\\grobid_error3.xml", "./tests/data\\grobid_error4.xml", "./tests/data\\grobid_error5.xml", "./tests/data\\pubmed.xml", "./tests/data\\test\\grobid.xml", "./tests/data\\test\\r1.xml", "./tests/data\\test\\test\\r2.xml"]
    
    doc_format = "arxiv"
    recursive = False
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control
    recursive = True
    files = locate_files(path, doc_format, recursive, compression)
    assert files == controlr
    
    doc_format = "grobid"
    recursive = False
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control
    recursive = True
    files = locate_files(path, doc_format, recursive, compression)
    assert files == controlr
    
    doc_format = "pubmed"
    recursive = False
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control
    recursive = True
    files = locate_files(path, doc_format, recursive, compression)
    assert files == controlr

    
    recursive = False
    compression = "zstd"
    doc_format = "pubmed"
    control = ["./tests/data\\2007-001.xml.zstd"]
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control
    compression = "gzip"
    doc_format = "bibtex"
    control = ["./tests/data\\bibtex_error.bib.gz"]
    files = locate_files(path, doc_format, recursive, compression)
    assert files == control

# def test_main():
#     main(doc_format, path, pdf, recursive, compression, update, batch_size)

# def test_parallel_main():
#     parallel_main(parallel, cluster, doc_format, path, pdf, recursive, compression, update, batch_size)
