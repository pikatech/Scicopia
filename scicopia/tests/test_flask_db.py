import pytest
from flask import g, session, request

import scicopia.app.db as db
from scicopia.app import create_app

from scicopia.app.main import main

@pytest.fixture
def app():
    app = create_app('testing')
    yield app

@main.route("/test_link", methods=["GET", "POST"])
def test_link():
    texts = ['Test1: wikipedia.org', 'Text ohne link']
    control = ['Test1: wikipedia.org', 'Text ohne link']
    output = db.link(texts)
    assert output == control

    texts = ['Test2: https://de.wikipedia.org/wiki/Wikipedia:Hauptseite', 'Text ohne link']
    control = ['Test2: <a href="https://de.wikipedia.org/wiki/Wikipedia:Hauptseite">https://de.wikipedia.org/wiki/Wikipedia:Hauptseite</a>', 'Text ohne link']
    output = db.link(texts)
    assert output == control

    texts = ['Test3: https://de.wikipedia.org mehr text', 'Text ohne link']
    control = ['Test3: <a href="https://de.wikipedia.org">https://de.wikipedia.org</a> mehr text', 'Text ohne link']
    output = db.link(texts)
    assert output == control

    texts = ['Test4: http://de.wikipedia.org mehr text', 'Text ohne link']
    control = ['Test4: <a href="http://de.wikipedia.org">http://de.wikipedia.org</a> mehr text', 'Text ohne link']
    output = db.link(texts)
    assert output == control

    texts = ['Test5: www.de.wikipedia.org mehr text', 'Text ohne link']
    control = ['Test5: www.de.wikipedia.org mehr text', 'Text ohne link']
    output = db.link(texts)
    assert output == control

    texts = ['Test6: https:/de.wikipedia.org mehr text', 'Text ohne link']
    control = ['Test6: https:/de.wikipedia.org mehr text', 'Text ohne link']
    output = db.link(texts)
    assert output == control
    return "0"
def test_link(app):
# link(texts: List[str])
    with app.test_client() as c:
        c.post('/test_link')

@main.route("/test_analyze_input", methods=["GET", "POST"])
def test_analyze_input():
    # adding of restrictions to must and must_not ist a known unsolved bug
    input = "time"
    control = {'must': [{'multi_match': {'query': 'time'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    
    input = "'time'"
    control = {'must': [{'multi_match': {'query': 'time', 'type': 'phrase'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    
    input = "time space"
    control = {'must': [{'multi_match': {'query': 'time'}}, {'multi_match': {'query': 'space'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    
    input = "'time space'"
    control = {'must': [{'multi_match': {'query': 'time space', 'type': 'phrase'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    
    input = "titel:time space"
    control = {'must': [{'match': {'titel': 'time'}}, {'multi_match': {'query': 'space'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    
    input = "titel:'time space'"
    control = {'must': [{'match_phrase': {'titel': 'time space'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control

    input = "-time"
    control = {'must': [], 'must_not': [{'multi_match': {'query': 'time'}}]}
    output = db.analyze_input(input)
    assert output == control
    
    input = "-time space"
    control = {'must': [{'multi_match': {'query': 'space'}}], 'must_not': [{'multi_match': {'query': 'time'}}]}
    output = db.analyze_input(input)
    assert output == control
    
    input = "-'time space'"
    control = {'must': [{'multi_match': {'query': 'time space', 'type': 'phrase'}}], 'must_not': [{'multi_match': {'query': 'time space', 'type': 'phrase'}}]}
    output = db.analyze_input(input)
    assert output == control
    
    input = "-titel:time space"
    control = {'must': [{'match': {'titel': 'time'}}, {'multi_match': {'query': 'space'}}], 'must_not': [{'match': {'titel': 'time'}}]}
    output = db.analyze_input(input)
    assert output == control
    
    input = "-titel:'time space'"
    control = {'must': [{'match_phrase': {'titel': 'time space'}}], 'must_not': [{'match_phrase': {'titel': 'time space'}}]}
    output = db.analyze_input(input)
    assert output == control
    
    input = "query:time"
    control = {'must': [{'match': {'query': 'time'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    
    input = "query:'time space'"
    control = {'must': [{'match_phrase': {'query': 'time space'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    
    input = "quer:time"
    control = {'must': [{'match': {'quer': 'time'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    
    input = "ta:time"
    control = {'must': [{'match': {'ta': 'time'}}], 'must_not': []}
    output = db.analyze_input(input)
    assert output == control
    return "0"
def test_analyze_input(app):
# analyze_input(input: str)
    with app.test_client() as c:
        c.post('/test_analyze_input')

@main.route("/test_checkFields", methods=["GET", "POST"])
def test_checkFields():
    fields = ['author', 'title', 'abstract', 'tags']

    condition = {'multi_match': {'query': 'time'}}
    control = ({'multi_match': {'query': 'time'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    
    condition = {'multi_match': {'query': 'time', 'type': 'phrase'}}
    control = ({'multi_match': {'query': 'time', 'type': 'phrase'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    
    condition = {'match': {'title': 'time'}}
    control = ({'match': {'title': 'time'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    
    condition = {'match': {'titel': 'time'}}
    control = ({'match': {'title': 'time'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    
    condition = {'match_phrase': {'titel': 'time space'}}
    control = ({'match_phrase': {'title': 'time space'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    
    condition = {'match': {'tag': 'time'}}
    control = ({'terms': {'tags': ['time']}}, "time")
    out = db.checkFields(condition, fields)
    assert out == control
    
    condition = {'match_phrase': {'tag': 'time space'}}
    control = ({'terms': {'tags': ['time space']}}, "time space")
    out = db.checkFields(condition, fields)
    assert out == control
    
    condition = {'match': {'query': 'time'}}
    control = ({'multi_match': {'query': 'time'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    
    condition = {'match_phrase': {'query': 'time space'}}
    control = ({'multi_match': {'query': 'time space', 'type': 'phrase'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    
    condition = {'match': {'quer': 'time'}}
    control = ({'multi_match': {'query': 'time'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    
    condition = {'match': {'ta': 'time'}}
    control = ({'multi_match': {'query': 'time'}}, False)
    out = db.checkFields(condition, fields)
    assert out == control
    return "0"
def test_checkFields(app):
# checkFields(condition, fields)
    with app.test_client() as c:
        c.post('/test_checkFields')

@main.route("/test_newsearch", methods=["GET", "POST"])
def test_newsearch():
    db.newsearch()
    return "0"
def test_newsearch(app):
# newsearch()
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Eingabe: "time"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'time'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "'time'"

        with c.session_transaction() as sess:
            # Eingabe: "'time'"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'time', 'type': 'phrase'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "'time'"
        
        with c.session_transaction() as sess:
            # Eingabe: "time space"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'time'}}, {'multi_match': {'query': 'space'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "'time' 'space'"
        
        with c.session_transaction() as sess:
            # Eingabe: "'time space'"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'time space', 'type': 'phrase'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "'time space'"
        
        with c.session_transaction() as sess:
            # Eingabe: "title: time space"
            sess["condition"] = {}
            sess['condition']['must'] = [{'match': {'title': 'time'}}, {'multi_match': {'query': 'space'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "title: 'time' 'space'"
        
        with c.session_transaction() as sess:
            # Eingabe: "title: 'time space"
            sess["condition"] = {}
            sess['condition']['must'] = [{'match_phrase': {'title': 'time space'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "title: 'time space'"
        
        with c.session_transaction() as sess:
            # Eingabe: "-time"
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'time'}}]
        c.post('/test_newsearch')
        assert session["query"] == "-'time'"
        
        with c.session_transaction() as sess:
            # Eingabe: "-time space"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'space'}}]
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'time'}}]
        c.post('/test_newsearch')
        assert session["query"] == "'space' -'time'"
        
        with c.session_transaction() as sess:
            # Eingabe: "-'time space'"
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'multi_match': {'query': 'time space', 'type': 'phrase'}}]
        c.post('/test_newsearch')
        assert session["query"] == "-'time space'"
        
        with c.session_transaction() as sess:
            # Eingabe: "-title:time space"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'space'}}]
            sess["condition"]["must_not"] = [{'match': {'title': 'time'}}]
        c.post('/test_newsearch')
        assert session["query"] == "'space' -title: 'time'"
        
        with c.session_transaction() as sess:
            # Eingabe: "-title:'time space'"
            sess["condition"] = {}
            sess['condition']['must'] = []
            sess["condition"]["must_not"] = [{'match_phrase': {'title': 'time space'}}]
        c.post('/test_newsearch')
        assert session["query"] == "-title: 'time space'"
        
        with c.session_transaction() as sess:
            # Eingabe: "tags: time space"
            sess["condition"] = {}
            sess['condition']['must'] = [{'terms': {'tags': ['time']}}, {'multi_match': {'query': 'space'}}]
            sess["condition"]["must_not"] = []
        c.post('/test_newsearch')
        assert session["query"] == "tags: 'time' 'space'"
        
        with c.session_transaction() as sess:
            # Eingabe: "-tags: time space"
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'space'}}]
            sess["condition"]["must_not"] = [{'terms': {'tags': ['time']}}]
        c.post('/test_newsearch')
        assert session["query"] == "'space' -tags: 'time'"
        
@main.route("/test_execute_query", methods=["GET", "POST"])
def test_execute_query():
    db.execute_query()
    return "0"
def test_execute_query(app):
# execute_query()
# TODO: find way to test g.hits and total_hits
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["condition"] = {}
            sess['condition']['must'] = [{'multi_match': {'query': 'time'}}]
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            sess["tags"] = []
        with app.app_context():
            c.post('/test_execute_query')
            print(g)
            assert g.hits
            print(session)
            assert session["showfulltext"] == False
            assert session["tags"]
            assert session["total_hits"]
            assert "time" in session

# @main.route("/test_add_search", methods=["GET", "POST"])
# def test_add_search():
#     db.add_search()
#     return "0"
# def test_add_search(app):
# # add_search(data)
#     with app.test_client() as c:
#         c.post('/test_add_search')

# @main.route("/test_verify_password", methods=["GET", "POST"])
# def test_verify_password():
#     db.verify_password()
#     return "0"
# def test_verify_password(app):
# # verify_password(user, password)
#     with app.test_client() as c:
#         c.post('/test_verify_password')

# @main.route("/test_reset_password", methods=["GET", "POST"])
# def test_reset_password():
#     db.reset_password()
#     return "0"
# def test_reset_password(app):
# # reset_password(token, new_password)
#     with app.test_client() as c:
#         c.post('/test_reset_password')

# @main.route("/test_generate_confirmation_token", methods=["GET", "POST"])
# def test_generate_confirmation_token():
#     db.generate_confirmation_token()
#     return "0"
# def test_generate_confirmation_token(app):
# # generate_confirmation_token(user, expiration=3600)
#     with app.test_client() as c:
#         c.post('/test_generate_confirmation_token')

# @main.route("/test_confirm_u", methods=["GET", "POST"])
# def test_confirm_u():
#     db.confirm_u()
#     return "0"
# def test_confirm_u(app):
# # confirm_u(user, token)
#     with app.test_client() as c:
#         c.post('/test_confirm_u')
