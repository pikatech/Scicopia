import pytest
import time
from flask import current_app, g, session, request
from werkzeug.security import generate_password_hash
from scicopia.tests.data.initFlaskData import main as init
init()#doc=True,elastic=True,user=True
import scicopia.app.db as db
from scicopia.app import create_app

from scicopia.app.main import main

@pytest.fixture
def app():
    app = create_app('testing')
    yield app


# link(texts: List[str])
@main.route("/test_link_https", methods=["GET", "POST"])
def link_https():
    texts = ['Test3: https://en.wikipedia.org more text.', 'Text without link.']
    control = ['Test3: <a href="https://en.wikipedia.org">https://en.wikipedia.org</a> more text.', 'Text without link.']
    output = db.link(texts)
    assert output == control
    return "0"
def test_link_https(app):
    with app.test_client() as c:
        c.post('/test_link_https')

@main.route("/test_link_https_long", methods=["GET", "POST"])
def link_https_long():
    texts = ['Test2: https://https://en.wikipedia.org/wiki/Main_Page', 'Text without link.']
    control = ['Test2: <a href="https://https://en.wikipedia.org/wiki/Main_Page">https://https://en.wikipedia.org/wiki/Main_Page</a>', 'Text without link.']
    output = db.link(texts)
    assert output == control
    return "0"
def test_link_https_long(app):
    with app.test_client() as c:
        c.post('/test_link_https_long')

@main.route("/test_link_http", methods=["GET", "POST"])
def link_http():
    texts = ['Test4: http://en.wikipedia.org more text.', 'Text without link.']
    control = ['Test4: <a href="http://en.wikipedia.org">http://en.wikipedia.org</a> more text.', 'Text without link.']
    output = db.link(texts)
    assert output == control
    return "0"
def test_link_http(app):
    with app.test_client() as c:
        c.post('/test_link_http')

@main.route("/test_link_wrong_http", methods=["GET", "POST"])
def link_wrong_http():
    texts = ['Test6: https:/en.wikipedia.org more text.', 'Text without link.']
    control = ['Test6: https:/en.wikipedia.org more text.', 'Text without link.']
    output = db.link(texts)
    assert output == control
    return "0"
def test_link_wrong_http(app):
    with app.test_client() as c:
        c.post('/test_link_wrong_http')

@main.route("/test_link_nohttp", methods=["GET", "POST"])
def link_nohttp():
    texts = ['Test1: wikipedia.org', 'Text without link.']
    control = ['Test1: wikipedia.org', 'Text without link.']
    output = db.link(texts)
    assert output == control
    return "0"
def test_link_nohttp(app):
    with app.test_client() as c:
        c.post('/test_link_nohttp')

@main.route("/test_link_www", methods=["GET", "POST"])
def link_www():
    texts = ['Test5: www.en.wikipedia.org more text.', 'Text without link.']
    control = ['Test5: www.en.wikipedia.org more text.', 'Text without link.']
    output = db.link(texts)
    assert output == control
    return "0"
def test_link_www(app):
    with app.test_client() as c:
        c.post('/test_link_www')


# analyze_input(input: str)
@main.route("/test_analyze_input_must_word", methods=["GET", "POST"])
def analyze_input_must_word():
    input = "lorem"
    control = {'must': [{'multi_match': {'query': 'lorem'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_word(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_word')
    
@main.route("/test_analyze_input_must_phrase", methods=["GET", "POST"])
def analyze_input_must_phrase():
    input = "'lorem'"
    control = {'must': [{'multi_match': {'query': 'lorem', 'type': 'phrase'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_phrase(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_phrase')
    
@main.route("/test_analyze_input_must_words", methods=["GET", "POST"])
def analyze_input_must_words():
    input = "lorem ipsum"
    control = {'must': [{'multi_match': {'query': 'lorem'}}, {'multi_match': {'query': 'ipsum'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_words(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_words')
    
@main.route("/test_analyze_input_must_phrase2", methods=["GET", "POST"])
def analyze_input_must_phrase2():
    input = "'lorem ipsum'"
    control = {'must': [{'multi_match': {'query': 'lorem ipsum', 'type': 'phrase'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_phrase2(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_phrase2')
    
@main.route("/test_analyze_input_must_word_title", methods=["GET", "POST"])
def analyze_input_must_word_title():
    input = "titel:lorem ipsum"
    control = {'must': [{'match': {'titel': 'lorem'}}, {'multi_match': {'query': 'ipsum'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_word_title(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_word_title')
    
@main.route("/test_analyze_input_must_title_phrase2", methods=["GET", "POST"])
def analyze_input_must_title_phrase2():
    input = "titel:'lorem ipsum'"
    control = {'must': [{'match_phrase': {'titel': 'lorem ipsum'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_title_phrase2(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_title_phrase2')
    
@main.route("/test_analyze_input_mustnot_word", methods=["GET", "POST"])
def analyze_input_mustnot_word():
    input = "-lorem"
    control = {'must': [], 'must_not': [{'multi_match': {'query': 'lorem'}}]}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_mustnot_word(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_mustnot_word')
    
@main.route("/test_analyze_input_mustnot_phrase", methods=["GET", "POST"])
def analyze_input_mustnot_phrase():
    # adding of restrictions to conditions is a known, unsolved, bug
    input = "-'lorem'"
    control = {'must': [], 'must_not': [{'multi_match': {'query': 'lorem', 'type': 'phrase'}}]}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_mustnot_phrase(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_mustnot_phrase')
    
@main.route("/test_analyze_input_must_word_mustnot_word", methods=["GET", "POST"])
def analyze_input_must_word_mustnot_word():
    input = "-lorem ipsum"
    control = {'must': [{'multi_match': {'query': 'ipsum'}}], 'must_not': [{'multi_match': {'query': 'lorem'}}]}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_word_mustnot_word(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_word_mustnot_word')
    
@main.route("/test_analyze_input_mustnot_phrase2", methods=["GET", "POST"])
def analyze_input_mustnot_phrase2():
    # adding of restrictions to conditions is a known, unsolved, bug
    input = "-'lorem ipsum'"
    control = {'must': [], 'must_not': [{'multi_match': {'query': 'lorem ipsum', 'type': 'phrase'}}]}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_mustnot_phrase2(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_mustnot_phrase2')
    
@main.route("/test_analyze_input_must_word_mustnot_title_word", methods=["GET", "POST"])
def analyze_input_must_word_mustnot_title_word():
    # adding of restrictions to conditions is a known, unsolved, bug
    input = "-titel:lorem ipsum"
    control = {'must': [{'multi_match': {'query': 'ipsum'}}], 'must_not': [{'match': {'titel': 'lorem'}}]}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_word_mustnot_title_word(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_word_mustnot_title_word')
    
@main.route("/test_analyze_input_mustnot_title_phrase2", methods=["GET", "POST"])
def analyze_input_mustnot_title_phrase2():
    # adding of restrictions to conditions is a known, unsolved, bug
    input = "-titel:'lorem ipsum'"
    control = {'must': [], 'must_not': [{'match_phrase': {'titel': 'lorem ipsum'}}]}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_mustnot_title_phrase2(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_mustnot_title_phrase2')
    
@main.route("/test_analyze_input_must_query_word", methods=["GET", "POST"])
def analyze_input_must_query_word():
    input = "query:lorem"
    control = {'must': [{'match': {'query': 'lorem'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_query_word(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_query_word')
    
@main.route("/test_analyze_input_must_query_phrase2", methods=["GET", "POST"])
def analyze_input_must_query_phrase2():
    input = "query:'lorem ipsum'"
    control = {'must': [{'match_phrase': {'query': 'lorem ipsum'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_query_phrase2(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_query_phrase2')
    
@main.route("/test_analyze_input_must_quer_word", methods=["GET", "POST"])
def analyze_input_must_quer_word():
    input = "quer:lorem"
    control = {'must': [{'match': {'quer': 'lorem'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_quer_word(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_quer_word')
    
@main.route("/test_analyze_input_must_ta_word", methods=["GET", "POST"])
def analyze_input_must_ta_word():
    input = "ta:lorem"
    control = {'must': [{'match': {'ta': 'lorem'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input_must_ta_word(app):
    with app.test_client() as c:
        c.post('/test_analyze_input_must_ta_word')


# checkFields(condition, fields)
@main.route("/test_checkFields_word", methods=["GET", "POST"])
def checkFields_word():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'multi_match': {'query': 'lorem'}}
    control = ({'multi_match': {'query': 'lorem'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_word(app):
    with app.test_client() as c:
        c.post('/test_checkFields_word')
    
@main.route("/test_checkFields_phrase", methods=["GET", "POST"])
def checkFields_phrase():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'multi_match': {'query': 'lorem', 'type': 'phrase'}}
    control = ({'multi_match': {'query': 'lorem', 'type': 'phrase'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_phrase(app):
    with app.test_client() as c:
        c.post('/test_checkFields_phrase')
    
@main.route("/test_checkFields_title_word", methods=["GET", "POST"])
def checkFields_title_word():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'match': {'title': 'lorem'}}
    control = ({'match': {'title': 'lorem'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_title_word(app):
    with app.test_client() as c:
        c.post('/test_checkFields_title_word')
    
@main.route("/test_checkFields_titel_word", methods=["GET", "POST"])
def checkFields_titel_word():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'match': {'titel': 'lorem'}}
    control = ({'match': {'title': 'lorem'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_titel_word(app):
    with app.test_client() as c:
        c.post('/test_checkFields_titel_word')
    
@main.route("/test_checkFields_titel_phrase2", methods=["GET", "POST"])
def checkFields_titel_phrase2():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'match_phrase': {'titel': 'lorem ipsum'}}
    control = ({'match_phrase': {'title': 'lorem ipsum'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_titel_phrase2(app):
    with app.test_client() as c:
        c.post('/test_checkFields_titel_phrase2')
    
@main.route("/test_checkFields_tag_word", methods=["GET", "POST"])
def checkFields_tag_word():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'match': {'tag': 'lorem'}}
    control = ({'terms': {'tags': ['lorem']}}, "lorem")
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_tag_word(app):
    with app.test_client() as c:
        c.post('/test_checkFields_tag_word')
    
@main.route("/test_checkFields_tag_phrase2", methods=["GET", "POST"])
def checkFields_tag_phrase2():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'match_phrase': {'tag': 'lorem ipsum'}}
    control = ({'terms': {'tags': ['lorem ipsum']}}, "lorem ipsum")
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_tag_phrase2(app):
    with app.test_client() as c:
        c.post('/test_checkFields_tag_phrase2')
    
@main.route("/test_checkFields_query_word", methods=["GET", "POST"])
def checkFields_query_word():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'match': {'query': 'lorem'}}
    control = ({'multi_match': {'query': 'lorem'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_query_word(app):
    with app.test_client() as c:
        c.post('/test_checkFields_query_word')
    
@main.route("/test_checkFields_query_phrase2", methods=["GET", "POST"])
def checkFields_query_phrase2():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'match_phrase': {'query': 'lorem ipsum'}}
    control = ({'multi_match': {'query': 'lorem ipsum', 'type': 'phrase'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_query_phrase2(app):
    with app.test_client() as c:
        c.post('/test_checkFields_query_phrase2')
    
@main.route("/test_checkFields_quer_phrase", methods=["GET", "POST"])
def checkFields_quer_phrase():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'match': {'quer': 'lorem'}}
    control = ({'multi_match': {'query': 'lorem'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_quer_phrase(app):
    with app.test_client() as c:
        c.post('/test_checkFields_quer_phrase')
    
@main.route("/test_checkFields_ta_word", methods=["GET", "POST"])
def checkFields_ta_word():
    fields = ['author', 'title', 'abstract', 'tags']
    condition = {'match': {'ta': 'lorem'}}
    control = ({'multi_match': {'query': 'lorem'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields_ta_word(app):
    with app.test_client() as c:
        c.post('/test_checkFields_ta_word')


# newsearch()
@main.route("/test_newsearch", methods=["GET", "POST"])
def newsearch():
    db.newsearch()
    return "0"
def test_newsearch_must_word(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "lorem"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "'lorem'"

def test_newsearch_must_phrase(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "'lorem'"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem', 'type': 'phrase'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "'lorem'"

def test_newsearch_must_words(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "lorem ipsum"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem'}}, {'multi_match': {'query': 'ipsum'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "'lorem' 'ipsum'"

def test_newsearch_must_phrase2(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "'lorem ipsum'"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem ipsum', 'type': 'phrase'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "'lorem ipsum'"

def test_newsearch_must_word_title_word(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "title: lorem ipsum"
            sess["condition"] = {}
            sess['condition']['must'] = [{'match': {'title': 'lorem'}}, {'multi_match': {'query': 'ipsum'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "title: 'lorem' 'ipsum'"

def test_newsearch_must_title_phrase(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "title: 'lorem ipsum'"
            sess["condition"] = {}
            sess['condition']['must'] = [{'match_phrase': {'title': 'lorem ipsum'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "title: 'lorem ipsum'"

def test_newsearch_mustnot_word(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "-lorem"
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'lorem'}}]
        c.post('/test_newsearch')
        assert session["query"] == "-'lorem'"

def test_newsearch_must_word_mustnot_word(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "-lorem ipsum"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'ipsum'}}]
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'lorem'}}]
        c.post('/test_newsearch')
        assert session["query"] == "'ipsum' -'lorem'"

def test_newsearch_mustnot_phrase2(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "-'lorem ipsum'"
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'lorem ipsum', 'type': 'phrase'}}]
        c.post('/test_newsearch')
        assert session["query"] == "-'lorem ipsum'"

def test_newsearch_must_word_mustnot_title_word(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "-title:lorem ipsum"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'ipsum'}}]
            sess["condition"]["must_not"] = [{'match': {'title': 'lorem'}}]
        c.post('/test_newsearch')
        assert session["query"] == "'ipsum' -title: 'lorem'"

def test_newsearch_mustnot_title_phrase2(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "-title:'lorem ipsum'"
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'match_phrase': {'title': 'lorem ipsum'}}]
        c.post('/test_newsearch')
        assert session["query"] == "-title: 'lorem ipsum'"

def test_newsearch_must_word_tags_word(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "tags: lorem ipsum"
            sess["condition"] = {}
            sess['condition']['must'] = [{'terms': {'tags': ['lorem']}}, {'multi_match': {'query': 'ipsum'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "tags: 'lorem' 'ipsum'"

def test_newsearch_must_word_mustnot_tags_word(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Input: "-tags: lorem ipsum"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'ipsum'}}]
            sess["condition"]["must_not"] = [{'terms': {'tags': ['lorem']}}]
        c.post('/test_newsearch')
        assert session["query"] == "'ipsum' -tags: 'lorem'"


# execute_query()
@main.route("/test_execute_query", methods=["GET", "POST"])
def execute_query():
    db.execute_query()
    return "0"
def test_execute_query_must_lorem(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem'}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'oai:arXiv.org:121518513', 'title': 'Lorem ipsum dolor', 'year': 2007, 'abstract': ['<b>Lorem</b> ipsum dolor sit amet, consetetur sadipscing elitr.']},
                {'id': '121518513', 'title': 'Lorem ipsum dolor', 'author': 'Lorem Ipsum and Lörem Ipßüm', 'editor': 'Lörem Ipßüm', 'year': 2020, 'abstract': ['<b>Lorem</b> ipsum dolor sit amet']},
                {'id': 'PMID121518513', 'title': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.', 'editor': 'Lorem Ipsum and Ipßüm Lörem', 'year': 2018, 'abstract': ['<b>Lorem</b> ipsum']},
                ]
            # print(session)
            assert session["condition"]["must"] == [{'multi_match': {'query': 'lorem'}}]
            assert session["condition"]["must_not"] == []
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'ipsum', 'nr': 3, 'mark': False},
                {'name': 'lorem', 'nr': 3, 'mark': False},
                {'name': 'dolor', 'nr': 2, 'mark': False},
                {'name': 'sadipscing', 'nr': 2, 'mark': False},
                {'name': 'aliquyam', 'nr': 1, 'mark': False},
                {'name': 'amet', 'nr': 1, 'mark': False},
                {'name': 'consetetur', 'nr': 1, 'mark': False},
                {'name': 'elitr', 'nr': 1, 'mark': False},
                {'name': 'invidunt', 'nr': 1, 'mark': False},
                {'name': 'labore', 'nr': 1, 'mark': False}
                ]
            assert session["total_hits"] == 3
            assert session["query"] == "'lorem'"
            assert "time" in session

def test_execute_query_must_lorem_10(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem'}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 10
            sess["to_hit"] = 20
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == []
            # print(session)
            assert session["condition"]["must"] == [{'multi_match': {'query': 'lorem'}}]
            assert session["condition"]["must_not"] == []
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'ipsum', 'nr': 3, 'mark': False},
                {'name': 'lorem', 'nr': 3, 'mark': False},
                {'name': 'dolor', 'nr': 2, 'mark': False},
                {'name': 'sadipscing', 'nr': 2, 'mark': False},
                {'name': 'aliquyam', 'nr': 1, 'mark': False},
                {'name': 'amet', 'nr': 1, 'mark': False},
                {'name': 'consetetur', 'nr': 1, 'mark': False},
                {'name': 'elitr', 'nr': 1, 'mark': False},
                {'name': 'invidunt', 'nr': 1, 'mark': False},
                {'name': 'labore', 'nr': 1, 'mark': False}
                ]
            assert session["total_hits"] == 3
            assert session["query"] == "'lorem'"
            assert "time" in session

def test_execute_query_must_tempor(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'tempor'}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': '121518513', 'title': 'Lorem ipsum dolor', 'author': 'Lorem Ipsum and Lörem Ipßüm', 'editor': 'Lörem Ipßüm', 'year': 2020, 'abstract': ['sed diam nonumy eirmod <b>tempor</b> invidunt ut labore et dolore magna aliquyam erat']}
                ]
            # print(session)
            assert session["condition"]["must"] == [{'multi_match': {'query': 'tempor'}}]
            assert session["condition"]["must_not"] == []
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'aliquyam', 'nr': 1, 'mark': False},
                {'name': 'dolor', 'nr': 1, 'mark': False},
                {'name': 'invidunt', 'nr': 1, 'mark': False},
                {'name': 'ipsum', 'nr': 1, 'mark': False},
                {'name': 'labore', 'nr': 1, 'mark': False},
                {'name': 'lorem', 'nr': 1, 'mark': False},
                {'name': 'magna', 'nr': 1, 'mark': False},
                {'name': 'sadipscing', 'nr': 1, 'mark': False},
                {'name': 'tempor', 'nr': 1, 'mark': False},
                {'name': 'voluptua', 'nr': 1, 'mark': False}
                ]
            assert session["total_hits"] == 1
            assert session["query"] == "'tempor'"
            assert "time" in session

def test_execute_query_must_tags_invidunt(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'terms': {'tags': ['invidunt']}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': '121518513', 'title': 'Lorem ipsum dolor', 'author': 'Lorem Ipsum and Lörem Ipßüm', 'editor': 'Lörem Ipßüm', 'year': 2020, 'abstract': ['Lorem ipsum dolor sit amet', 'consetetur sadipscing elitr', 'sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat', 'sed diam voluptua']}
                ]
            # print(session)
            assert session["condition"]["must"] == [{'terms': {'tags': ['invidunt']}}]
            assert session["condition"]["must_not"] == []
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'aliquyam', 'nr': 1, 'mark': False},
                {'name': 'dolor', 'nr': 1, 'mark': False},
                {'name': 'invidunt', 'nr': 1, 'mark': True},
                {'name': 'ipsum', 'nr': 1, 'mark': False},
                {'name': 'labore', 'nr': 1, 'mark': False},
                {'name': 'lorem', 'nr': 1, 'mark': False},
                {'name': 'magna', 'nr': 1, 'mark': False},
                {'name': 'sadipscing', 'nr': 1, 'mark': False},
                {'name': 'tempor', 'nr': 1, 'mark': False},
                {'name': 'voluptua', 'nr': 1, 'mark': False}
                ]
            assert session["total_hits"] == 1
            assert session["query"] == "tags: 'invidunt'"
            assert "time" in session

def test_execute_query_must_dolor_tags_lorem(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'terms': {'tags': ['lorem']}}, {'multi_match': {'query': 'dolor'}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'oai:arXiv.org:121518513', 'title': 'Lorem ipsum dolor', 'year': 2007, 'abstract': ['Lorem ipsum <b>dolor</b> sit amet, consetetur sadipscing elitr.']},
                {'id': '121518513', 'title': 'Lorem ipsum dolor', 'author': 'Lorem Ipsum and Lörem Ipßüm', 'editor': 'Lörem Ipßüm', 'year': 2020, 'abstract': ['Lorem ipsum <b>dolor</b> sit amet']},
                {'id': 'PMID121518513', 'title': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.', 'editor': 'Lorem Ipsum and Ipßüm Lörem', 'year': 2018, 'abstract': ['Lorem ipsum']}
                ]
            # print(session)
            assert session["condition"]["must"] == [{'terms': {'tags': ['lorem']}}, {'multi_match': {'query': 'dolor'}}]
            assert session["condition"]["must_not"] == []
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'ipsum', 'nr': 3, 'mark': False},
                {'name': 'lorem', 'nr': 3, 'mark': True},
                {'name': 'dolor', 'nr': 2, 'mark': False},
                {'name': 'sadipscing', 'nr': 2, 'mark': False},
                {'name': 'aliquyam', 'nr': 1, 'mark': False},
                {'name': 'amet', 'nr': 1, 'mark': False},
                {'name': 'consetetur', 'nr': 1, 'mark': False},
                {'name': 'elitr', 'nr': 1, 'mark': False},
                {'name': 'invidunt', 'nr': 1, 'mark': False},
                {'name': 'labore', 'nr': 1, 'mark': False}
                ]
            assert session["total_hits"] == 3
            assert session["query"] == "tags: 'lorem' 'dolor'"
            assert "time" in session

def test_execute_query_must_title_lorem(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'match_phrase': {'title': 'lorem'}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'oai:arXiv.org:121518513', 'title': 'Lorem ipsum dolor', 'year': 2007, 'abstract': ['Lorem ipsum dolor sit amet, consetetur sadipscing elitr.']},
                {'id': '121518513', 'title': 'Lorem ipsum dolor', 'author': 'Lorem Ipsum and Lörem Ipßüm', 'editor': 'Lörem Ipßüm', 'year': 2020, 'abstract': ['Lorem ipsum dolor sit amet', 'consetetur sadipscing elitr', 'sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat', 'sed diam voluptua']},
                {'id': 'PMID121518513', 'title': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.', 'editor': 'Lorem Ipsum and Ipßüm Lörem', 'year': 2018, 'abstract': ['Lorem ipsum']}
                ]
            # print(session)
            assert session["condition"]["must"] == [{'match_phrase': {'title': 'lorem'}}]
            assert session["condition"]["must_not"] == []
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'ipsum', 'nr': 3, 'mark': False},
                {'name': 'lorem', 'nr': 3, 'mark': False},
                {'name': 'dolor', 'nr': 2, 'mark': False},
                {'name': 'sadipscing', 'nr': 2, 'mark': False},
                {'name': 'aliquyam', 'nr': 1, 'mark': False},
                {'name': 'amet', 'nr': 1, 'mark': False},
                {'name': 'consetetur', 'nr': 1, 'mark': False},
                {'name': 'elitr', 'nr': 1, 'mark': False},
                {'name': 'invidunt', 'nr': 1, 'mark': False},
                {'name': 'labore', 'nr': 1, 'mark': False}
                ]
            assert session["total_hits"] == 3
            assert session["query"] == "title: 'lorem'"
            assert "time" in session

def test_execute_query_must_author_lörem(app):
    with app.test_client() as c:
        # the problem to search on author is a known, unsolved, bug
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'match_phrase': {'author': 'lörem'}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'Lorem', 'title': 'voluptua', 'author': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'editor': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'year': 2019},
                {'id': '121518513', 'title': 'Lorem ipsum dolor', 'author': 'Lorem Ipsum and Lörem Ipßüm', 'editor': 'Lörem Ipßüm', 'year': 2020, 'abstract': ['Lorem ipsum dolor sit amet', 'consetetur sadipscing elitr', 'sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat', 'sed diam voluptua']},
            ]
            # print(session)
            assert session["condition"]["must"] == [{'match_phrase': {'author': 'lörem'}}]
            assert session["condition"]["must_not"] == []
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'ipsum', 'nr': 1, 'mark': False},
                {'name': 'lorem', 'nr': 1, 'mark': False},
                {'name': 'dolor', 'nr': 1, 'mark': False},
                {'name': 'tempor', 'nr': 1, 'mark': False},
                {'name': 'invidunt', 'nr': 1, 'mark': False},
                {'name': 'labore', 'nr': 1, 'mark': False},
                {'name': 'magna', 'nr': 1, 'mark': False},
                {'name': 'voluptua', 'nr': 1, 'mark': False},
                {'name': 'sadipscing', 'nr': 1, 'mark': False},
                {'name': 'aliquyam', 'nr': 1, 'mark': False}
            ]
            assert session["total_hits"] == 2
            assert session["query"] == "author: 'lörem'"
            assert "time" in session

def test_execute_query_mustnot_lorem(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'lorem'}}]
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'Lorem', 'title': 'voluptua', 'author': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'editor': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'year': 2019},
                {'id': 'Ipsum2019a', 'author': 'Lorem Ipsum', 'editor': 'Lorem Ipsum and Lörem Ipßüm', 'year': 2019},
                {'id': 'miss', 'title': 'Miss'}
                ]
            # print(session)
            assert session["condition"]["must"] == []
            assert session["condition"]["must_not"] == [{'multi_match': {'query': 'lorem'}}]
            assert session["showfulltext"] == False
            assert session["tags"] == []
            assert session["total_hits"] == 3
            assert session["query"] == "-'lorem'"
            assert "time" in session

def test_execute_query_mustnot_lorem_10(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'lorem'}}]
            sess["from_hit"] = 10
            sess["to_hit"] = 20
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == []
            # print(session)
            assert session["condition"]["must"] == []
            assert session["condition"]["must_not"] == [{'multi_match': {'query': 'lorem'}}]
            assert session["showfulltext"] == False
            assert session["tags"] == []
            assert session["total_hits"] == 3
            assert session["query"] == "-'lorem'"
            assert "time" in session

def test_execute_query_mustnot_tempor(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'tempor'}}]
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'oai:arXiv.org:121518513', 'title': 'Lorem ipsum dolor', 'year': 2007, 'abstract': ['Lorem ipsum dolor sit amet, consetetur sadipscing elitr.']},
                {'id': 'Lorem', 'title': 'voluptua', 'author': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'editor': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'year': 2019},
                {'id': 'Ipsum2019a', 'author': 'Lorem Ipsum', 'editor': 'Lorem Ipsum and Lörem Ipßüm', 'year': 2019},
                {'id': 'PMID121518513', 'title': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.', 'editor': 'Lorem Ipsum and Ipßüm Lörem', 'year': 2018, 'abstract': ['Lorem ipsum']},
                {'id': 'miss', 'title': 'Miss'}
                ]
            # print(session)
            assert session["condition"]["must"] == []
            assert session["condition"]["must_not"] == [{'multi_match': {'query': 'tempor'}}]
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'ipsum', 'nr': 2, 'mark': False},
                {'name': 'lorem', 'nr': 2, 'mark': False},
                {'name': 'amet', 'nr': 1, 'mark': False},
                {'name': 'consetetur', 'nr': 1, 'mark': False},
                {'name': 'dolor', 'nr': 1, 'mark': False},
                {'name': 'elitr', 'nr': 1, 'mark': False},
                {'name': 'sadipscing', 'nr': 1, 'mark': False},
                {'name': 'sit', 'nr': 1, 'mark': False}]
            assert session["total_hits"] == 5
            assert session["query"] == "-'tempor'"
            assert "time" in session

def test_execute_query_mustnot_tags_invidunt(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'terms': {'tags': ['invidunt']}}]
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'oai:arXiv.org:121518513', 'title': 'Lorem ipsum dolor', 'year': 2007, 'abstract': ['Lorem ipsum dolor sit amet, consetetur sadipscing elitr.']},
                {'id': 'Lorem', 'title': 'voluptua', 'author': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'editor': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'year': 2019},
                {'id': 'Ipsum2019a', 'author': 'Lorem Ipsum', 'editor': 'Lorem Ipsum and Lörem Ipßüm', 'year': 2019},
                {'id': 'PMID121518513', 'title': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.', 'editor': 'Lorem Ipsum and Ipßüm Lörem', 'year': 2018, 'abstract': ['Lorem ipsum']},
                {'id': 'miss', 'title': 'Miss'}
            ]
            # print(session)
            assert session["condition"]["must"] == []
            assert session["condition"]["must_not"] == [{'terms': {'tags': ['invidunt']}}]
            assert session["showfulltext"] == False
            assert session["tags"] == [{'name': 'ipsum', 'nr': 2, 'mark': False},
                {'name': 'lorem', 'nr': 2, 'mark': False},
                {'name': 'amet', 'nr': 1, 'mark': False},
                {'name': 'consetetur', 'nr': 1, 'mark': False},
                {'name': 'dolor', 'nr': 1, 'mark': False},
                {'name': 'elitr', 'nr': 1, 'mark': False},
                {'name': 'sadipscing', 'nr': 1, 'mark': False},
                {'name': 'sit', 'nr': 1, 'mark': False}]
            assert session["total_hits"] == 5
            assert session["query"] == "-tags: 'invidunt'"
            assert "time" in session

def test_execute_query_mustnot_dolor_tags_lorem(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'terms': {'tags': ['lorem']}}, {'multi_match': {'query': 'dolor'}}]
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'Lorem', 'title': 'voluptua', 'author': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'editor': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'year': 2019},
                {'id': 'Ipsum2019a', 'author': 'Lorem Ipsum', 'editor': 'Lorem Ipsum and Lörem Ipßüm', 'year': 2019},
                {'id': 'miss', 'title': 'Miss'}
            ]
            # print(session)
            assert session["condition"]["must"] == []
            assert session["condition"]["must_not"] == [{'terms': {'tags': ['lorem']}}, {'multi_match': {'query': 'dolor'}}]
            assert session["showfulltext"] == False
            assert session["tags"] == []
            assert session["total_hits"] == 3
            assert session["query"] == "-tags: 'lorem' -'dolor'"
            assert "time" in session

def test_execute_query_mustnot_title_lorem(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'match_phrase': {'title': 'lorem'}}]
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'Lorem', 'title': 'voluptua', 'author': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'editor': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'year': 2019},
                {'id': 'Ipsum2019a', 'author': 'Lorem Ipsum', 'editor': 'Lorem Ipsum and Lörem Ipßüm', 'year': 2019},
                {'id': 'miss', 'title': 'Miss'}
            ]
            # print(session)
            assert session["condition"]["must"] == []
            assert session["condition"]["must_not"] == [{'match_phrase': {'title': 'lorem'}}]
            assert session["showfulltext"] == False
            assert session["tags"] == []
            assert session["total_hits"] == 3
            assert session["query"] == "-title: 'lorem'"
            assert "time" in session

def test_execute_query_mustnot_author_lörem(app):
    with app.test_client() as c:
        # the problem to search on author is a known, unsolved, bug
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'match_phrase': {'author': 'lörem'}}]
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'oai:arXiv.org:121518513', 'title': 'Lorem ipsum dolor', 'year': 2007, 'abstract': ['Lorem ipsum dolor sit amet, consetetur sadipscing elitr.']},
                {'id': 'Ipsum2019a', 'author': 'Lorem Ipsum', 'editor': 'Lorem Ipsum and Lörem Ipßüm', 'year': 2019},
                {'id': 'PMID121518513', 'title': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.', 'editor': 'Lorem Ipsum and Ipßüm Lörem', 'year': 2018, 'abstract': ['Lorem ipsum']},
                {'id': 'miss', 'title': 'Miss'}
            ]
            # print(session)
            assert session["condition"]["must"] == []
            assert session["condition"]["must_not"] == [{'match_phrase': {'author': 'lörem'}}]
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'ipsum', 'nr': 2, 'mark': False},
                {'name': 'lorem', 'nr': 2, 'mark': False},
                {'name': 'dolor', 'nr': 1, 'mark': False},
                {'name': 'sadipscing', 'nr': 1, 'mark': False},
                {'name': 'amet', 'nr': 1, 'mark': False},
                {'name': 'consetetur', 'nr': 1, 'mark': False},
                {'name': 'elitr', 'nr': 1, 'mark': False},
                {'name': 'sit', 'nr': 1, 'mark': False}
            ]
            assert session["total_hits"] == 4
            assert session["query"] == "-author: 'lörem'"
            assert "time" in session

def test_execute_query_must_lorem_mustnot_lorem(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem'}}]
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'lorem'}}]
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'Lorem', 'title': 'voluptua', 'author': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'editor': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'year': 2019},
                {'id': 'Ipsum2019a', 'author': 'Lorem Ipsum', 'editor': 'Lorem Ipsum and Lörem Ipßüm', 'year': 2019},
                {'id': 'miss', 'title': 'Miss'}
            ]
            # print(session)
            assert session["condition"]["must"] == []
            assert session["condition"]["must_not"] == [{'multi_match': {'query': 'lorem'}}]
            assert session["showfulltext"] == False
            assert session["tags"] == []
            assert session["total_hits"] == 3
            assert session["query"] == "-'lorem'"
            assert "time" in session

def test_execute_query_must_lorem_lorem_lorem_mustnot_lorem(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem'}},{'multi_match': {'query': 'lorem'}},{'multi_match': {'query': 'lorem'}}]
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'lorem'}}]
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'Lorem', 'title': 'voluptua', 'author': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'editor': 'Lorem Ipsum, Lörem Ipßüm and Sadipscing Elitr', 'year': 2019},
                {'id': 'Ipsum2019a', 'author': 'Lorem Ipsum', 'editor': 'Lorem Ipsum and Lörem Ipßüm', 'year': 2019},
                {'id': 'miss', 'title': 'Miss'}
            ]
            # print(session)
            assert session["condition"]["must"] == []
            assert session["condition"]["must_not"] == [{'multi_match': {'query': 'lorem'}}]
            assert session["showfulltext"] == False
            assert session["tags"] == []
            assert session["total_hits"] == 3
            assert session["query"] == "-'lorem'"
            assert "time" in session

def test_execute_query_must_lorem_ipsum_lorem_mustnot_lorem(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem'}},{'multi_match': {'query': 'ipsum'}},{'multi_match': {'query': 'lorem'}}]
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'lorem'}}]
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == []
            # print(session)
            assert session["condition"]["must"] == [{'multi_match': {'query': 'ipsum'}}]
            assert session["condition"]["must_not"] == [{'multi_match': {'query': 'lorem'}}]
            assert session["showfulltext"] == False
            assert session["tags"] == []
            assert session["total_hits"] == 0
            assert session["query"] == "'ipsum' -'lorem'"
            assert "time" in session

def test_execute_query_order_None(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem'}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
            sess["order"] = None
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'oai:arXiv.org:121518513', 'title': 'Lorem ipsum dolor', 'year': 2007, 'abstract': ['<b>Lorem</b> ipsum dolor sit amet, consetetur sadipscing elitr.']},
                {'id': '121518513', 'title': 'Lorem ipsum dolor', 'author': 'Lorem Ipsum and Lörem Ipßüm', 'editor': 'Lörem Ipßüm', 'year': 2020, 'abstract': ['<b>Lorem</b> ipsum dolor sit amet']},
                {'id': 'PMID121518513', 'title': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.', 'editor': 'Lorem Ipsum and Ipßüm Lörem', 'year': 2018, 'abstract': ['<b>Lorem</b> ipsum']},
                ]
            # print(session)
            assert session["condition"]["must"] == [{'multi_match': {'query': 'lorem'}}]
            assert session["condition"]["must_not"] == []
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'ipsum', 'nr': 3, 'mark': False},
                {'name': 'lorem', 'nr': 3, 'mark': False},
                {'name': 'dolor', 'nr': 2, 'mark': False},
                {'name': 'sadipscing', 'nr': 2, 'mark': False},
                {'name': 'aliquyam', 'nr': 1, 'mark': False},
                {'name': 'amet', 'nr': 1, 'mark': False},
                {'name': 'consetetur', 'nr': 1, 'mark': False},
                {'name': 'elitr', 'nr': 1, 'mark': False},
                {'name': 'invidunt', 'nr': 1, 'mark': False},
                {'name': 'labore', 'nr': 1, 'mark': False}
                ]
            assert session["total_hits"] == 3
            assert session["query"] == "'lorem'"
            assert "time" in session

def test_execute_query_order_asc(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem'}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
            sess["order"] = "asc"
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': 'oai:arXiv.org:121518513', 'title': 'Lorem ipsum dolor', 'year': 2007, 'abstract': ['<b>Lorem</b> ipsum dolor sit amet, consetetur sadipscing elitr.']},
                {'id': 'PMID121518513', 'title': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.', 'editor': 'Lorem Ipsum and Ipßüm Lörem', 'year': 2018, 'abstract': ['<b>Lorem</b> ipsum']},
                {'id': '121518513', 'title': 'Lorem ipsum dolor', 'author': 'Lorem Ipsum and Lörem Ipßüm', 'editor': 'Lörem Ipßüm', 'year': 2020, 'abstract': ['<b>Lorem</b> ipsum dolor sit amet']}
                ]
            # print(session)
            assert session["condition"]["must"] == [{'multi_match': {'query': 'lorem'}}]
            assert session["condition"]["must_not"] == []
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'ipsum', 'nr': 3, 'mark': False},
                {'name': 'lorem', 'nr': 3, 'mark': False},
                {'name': 'dolor', 'nr': 2, 'mark': False},
                {'name': 'sadipscing', 'nr': 2, 'mark': False},
                {'name': 'aliquyam', 'nr': 1, 'mark': False},
                {'name': 'amet', 'nr': 1, 'mark': False},
                {'name': 'consetetur', 'nr': 1, 'mark': False},
                {'name': 'elitr', 'nr': 1, 'mark': False},
                {'name': 'invidunt', 'nr': 1, 'mark': False},
                {'name': 'labore', 'nr': 1, 'mark': False}
                ]
            assert session["total_hits"] == 3
            assert session["query"] == "'lorem'"
            assert "time" in session

def test_execute_query_order_desc(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'lorem'}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
            sess["order"] = "desc"
        with app.app_context():
            c.post('/test_execute_query')
            # print(g.hits)
            assert g.hits == [
                {'id': '121518513', 'title': 'Lorem ipsum dolor', 'author': 'Lorem Ipsum and Lörem Ipßüm', 'editor': 'Lörem Ipßüm', 'year': 2020, 'abstract': ['<b>Lorem</b> ipsum dolor sit amet']},
                {'id': 'PMID121518513', 'title': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.', 'editor': 'Lorem Ipsum and Ipßüm Lörem', 'year': 2018, 'abstract': ['<b>Lorem</b> ipsum']},
                {'id': 'oai:arXiv.org:121518513', 'title': 'Lorem ipsum dolor', 'year': 2007, 'abstract': ['<b>Lorem</b> ipsum dolor sit amet, consetetur sadipscing elitr.']}
                ]
            # print(session)
            assert session["condition"]["must"] == [{'multi_match': {'query': 'lorem'}}]
            assert session["condition"]["must_not"] == []
            assert session["showfulltext"] == False
            assert session["tags"] == [
                {'name': 'ipsum', 'nr': 3, 'mark': False},
                {'name': 'lorem', 'nr': 3, 'mark': False},
                {'name': 'dolor', 'nr': 2, 'mark': False},
                {'name': 'sadipscing', 'nr': 2, 'mark': False},
                {'name': 'aliquyam', 'nr': 1, 'mark': False},
                {'name': 'amet', 'nr': 1, 'mark': False},
                {'name': 'consetetur', 'nr': 1, 'mark': False},
                {'name': 'elitr', 'nr': 1, 'mark': False},
                {'name': 'invidunt', 'nr': 1, 'mark': False},
                {'name': 'labore', 'nr': 1, 'mark': False}
                ]
            assert session["total_hits"] == 3
            assert session["query"] == "'lorem'"
            assert "time" in session
        # assert False


# add_search(data)
@main.route("/test_add_search/<data>", methods=["GET", "POST"])
def add_search(data):
    db.add_search(data)
    return "0"

def test_add_search(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["user"] = "no user"
        c.post('/test_add_search/Lorem')
        assert session["user"] is None

def test_add_search_loggedIn(app):
    with app.test_client() as c:
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
        with c.session_transaction() as sess:
            sess["user"] = "exists"
        try:
            c.post('/test_add_search/Lorem')
            assert session["user"] == "exists"
            assert collection["exists"]["lastsearch"] == ["Lorem"]
            c.post('/test_add_search/Ipsum')
            assert session["user"] == "exists"
            assert collection["exists"]["lastsearch"] == ["Lorem", "Ipsum"]
            c.post('/test_add_search/Lorem')
            assert session["user"] == "exists"
            assert collection["exists"]["lastsearch"] == ["Ipsum", "Lorem"]
            c.post('/test_add_search/lorem')
            assert session["user"] == "exists"
            assert collection["exists"]["lastsearch"] == ["Ipsum", "Lorem", "lorem"]
            c.post('/test_add_search/loreM')
            assert session["user"] == "exists"
            assert collection["exists"]["lastsearch"] == ["Ipsum", "Lorem", "lorem", "loreM"]
            c.post('/test_add_search/ipsum')
            assert session["user"] == "exists"
            assert collection["exists"]["lastsearch"] == ["Ipsum", "Lorem", "lorem", "loreM", "ipsum"]
            c.post('/test_add_search/Ipsum')
            assert session["user"] == "exists"
            assert collection["exists"]["lastsearch"] == ["Lorem", "lorem", "loreM", "ipsum", "Ipsum"]
        finally:
            doc = collection["exists"]
            doc["lastsearch"] = []
            doc.save()


# verify_password(user, password)
@main.route("/test_verify_password_UserNoUser", methods=["GET", "POST"])
def verify_password_UserNoUser():
    login = db.verify_password("no user", "password")
    assert not login
    return "0"
def test_verify_password_UserNoUser(app):
    with app.test_client() as c:
        c.post('/test_verify_password_UserNoUser')

@main.route("/test_verify_password_wrong_password", methods=["GET", "POST"])
def verify_password_wrong_password():
    login = db.verify_password("exists", "wrong password")
    assert not login
    return "0"
def test_verify_password_wrong_password(app):
    with app.test_client() as c:
        c.post('/test_verify_password_wrong_password')

@main.route("/test_verify_password_successfully", methods=["GET", "POST"])
def verify_password_successfully():
    login = db.verify_password("exists", "test")
    assert login
    return "0"
def test_verify_password_successfully(app):
    with app.test_client() as c:
        c.post('/test_verify_password_successfully')


# generate_confirmation_token(user, expiration=3600)
# confirm_u(user, token)
@main.route("/test_confirm_u_noToken", methods=["GET", "POST"])
def confirm_u_noToken():
    confirm = db.confirm_u("exists", "no token")
    assert not confirm
    return "0"
def test_confirm_u_noToken(app):
    with app.test_client() as c:
        c.post('/test_confirm_u_noToken')

@main.route("/test_confirm_u_expiredToken", methods=["GET", "POST"])
def confirm_u_expiredToken():
    token = db.generate_confirmation_token("exists", 1)
    time.sleep(2)
    confirm = db.confirm_u("exists", token)
    assert not confirm
    return "0"
def test_confirm_u_expiredToken(app):
    with app.test_client() as c:
        c.post('/test_confirm_u_expiredToken')
    
@main.route("/test_confirm_u_wrong_user", methods=["GET", "POST"])
def confirm_u_wrong_user():
    token = db.generate_confirmation_token("no user")
    confirm = db.confirm_u("exists", token)
    assert not confirm
    return "0"
def test_confirm_u_wrong_user(app):
    with app.test_client() as c:
        c.post('/test_confirm_u_wrong_user')
    
@main.route("/test_confirm_u_no_user", methods=["GET", "POST"])
def confirm_u_no_user():
    token = db.generate_confirmation_token("no user")
    confirm = db.confirm_u("no user", token)
    assert not confirm
    return "0"
def test_confirm_u_no_user(app):
    with app.test_client() as c:
        c.post('/test_confirm_u_no_user')
    
@main.route("/test_confirm_u_successfully", methods=["GET", "POST"])
def confirm_u_successfully():
    try:
        assert not current_app.config["USERCOLLECTION"]["exists"]["confirmed"]
        token = db.generate_confirmation_token("exists")
        confirm = db.confirm_u("exists", token)
        assert confirm
        assert current_app.config["USERCOLLECTION"]["exists"]["confirmed"]
    finally:
        doc = current_app.config["USERCOLLECTION"]["exists"]
        doc["confirmed"] = False
        doc.save()
    return "0"
def test_confirm_u_successfully(app):
    with app.test_client() as c:
        c.post('/test_confirm_u_successfully')


# generate_confirmation_token(user, expiration=3600)
# reset_password(token, new_password)
@main.route("/test_reset_password_noToken", methods=["GET", "POST"])
def reset_password_noToken():
    reset = db.reset_password("no token", "new_password")
    assert not reset
    return "0"
def test_reset_password_noToken(app):
    with app.test_client() as c:
        c.post('/test_reset_password_noToken')

@main.route("/test_reset_password_no_user", methods=["GET", "POST"])
def reset_password_no_user():
    token = db.generate_confirmation_token("no user")
    reset = db.reset_password(token, "new_password")
    assert not reset
    return "0"
def test_reset_password_no_user(app):
    with app.test_client() as c:
        c.post('/test_reset_password_no_user')

@main.route("/test_reset_password_expiredToken", methods=["GET", "POST"])
def reset_password_expiredToken():
    token = db.generate_confirmation_token("exists", 1)
    time.sleep(2)
    reset = db.reset_password(token, "new_password")
    assert not reset
    return "0"
def test_reset_password_expiredToken(app):
    with app.test_client() as c:
        c.post('/test_reset_password_expiredToken')

@main.route("/test_reset_password_successfully", methods=["GET", "POST"])
def reset_password_successfully():
    token = db.generate_confirmation_token("exists")
    reset = db.reset_password(token, "new_password")
    try:
        assert reset
    finally:
        doc = current_app.config["USERCOLLECTION"]["exists"]
        doc["password_hash"] = generate_password_hash("test")
        doc.save()
    return "0"
def test_reset_password_successfully(app):
    with app.test_client() as c:
        c.post('/test_reset_password_successfully')
