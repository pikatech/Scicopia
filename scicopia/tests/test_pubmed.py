from parsers.pubmed import *

def test_extract_abstract():
    source = "tests/data/pubmed.xml"
    context = iterparse(source, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)

    for event, elem in context:
        article = dict()
        if event == "end" and elem.tag == "PubmedArticle":

            abstract = elem.find(".//Abstract")
            # Abstract is optional
            if abstract is not None and abstract.text is not None:
                abstract = extract_abstract(abstract)
                if abstract is not None:
                    article["abstract"] = abstract
                    assert "abstract" in article
                    assert article["abstract"] == "Statin intolerance" or article["abstract"] == "Statin\nintolerance" or article["abstract"] == "Statin <b>intolerance<b>" or article["abstract"] == "Title: Statin intolerance" or article["abstract"] == "Title: Statin <b>intolerance<b>"

def test_extract_authors():
    source = "tests/data/pubmed.xml"
    context = iterparse(source, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)

    for event, elem in context:
        article = dict()
        if event == "end" and elem.tag == "PubmedArticle":

            authors = elem.find(".//AuthorList")
            # List of authors is optional
            if authors is not None and authors.text is not None:
                authors = extract_authors(authors)
                if authors:
                    article["author"] = authors
                    assert article["author"] == ['Julia Schreml', 'Ioanna Gouni-Berthold'] or article["author"] == ['J Schreml', 'I Gouni-Berthold'] or article["author"] == ['Julia Schreml', 'Ioanna Gouni-Berthold', 'et al.']

def test_extract_journaldata():
    source = "tests/data/pubmed.xml"
    context = iterparse(source, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)

    for event, elem in context:
        article = dict()
        if event == "end" and elem.tag == "PubmedArticle":
            pmid = "test"

            journal = elem.find(".//Journal")
            # journal entry is mandatory
            if journal is not None and journal.text is not None:
                article.update(extract_journaldata(journal, pmid))
            else:
                logging.warning("Article %s should have had a journal entry", pmid)
                continue

            if "volume" in article:
                assert article["volume"] == '25'

            if "issue" in article:
                assert article["issue"] == '13'

            if 'date' in article:
                assert article['date'] == '03/03/2018'

            if 'year' in article:
                assert article['year'] == '2018'

            if 'month' in article:
                assert article['month'] == 'march'

            if 'journal' in article:
                assert article['journal'] == 'Current medicinal chemistry'

def test_extract_mesh_headings():
    source = "tests/data/pubmed.xml"
    context = iterparse(source, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)

    for event, elem in context:
        article = dict()
        if event == "end" and elem.tag == "PubmedArticle":
            pmid = "test"

            mesh_headings = elem.find(".//MeshHeadingList")
            # List of authors is optional
            if mesh_headings is not None and mesh_headings.text is not None:
                mesh = extract_mesh_headings(mesh_headings, pmid)
                if mesh:
                    article["mesh"] = mesh

                    assert article["mesh"] == ['Antibodies, Monoclonal', 'Antibodies, Monoclonal, Humanized']

def test_parse():  # TODO: add controll of exceptions
    source = "tests/data/pubmed.xml"
    with open(source) as data:
        for datadict in parse(data):
            assert "PMID" in datadict
            assert datadict["PMID"] == '28618900'

            assert "Version" in datadict
            assert datadict["Version"] == '1'

            assert "url" in datadict
            assert datadict["url"] == "https://www.ncbi.nlm.nih.gov/pubmed/28618900"

            assert "title" in datadict
            assert datadict["title"] == "Role of Anti-PCSK9 Antibodies in the Treatment of Patients with Statin Intolerance." or datadict["title"] == "Role of <b>Anti-PCSK9 Antibodies<b> in the Treatment of Patients with Statin Intolerance."
