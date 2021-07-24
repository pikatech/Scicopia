import pytest
from flask import current_app, g, session, request
from scicopia.tests.data.initFlaskData import main as init
init()#doc=True,elastic=True,pdf=True,user=True

from scicopia.app import create_app

@pytest.fixture
def app():
    app = create_app('testing')
    yield app


def test_navbar(app):
    with app.test_client() as c:
        rv = c.post('/', follow_redirects=True).data
        print(rv)
        # # check for page elements
        assert b'navbar' in rv
        assert b'fixed-top' in rv
        assert b'<a class="navbar-brand" href="/">' in rv
        assert b'<button class="navbar-toggler" type="button" data-toggle="collapse"' in rv
        assert b'<a class="nav-link" href="/">' in rv
        assert b'<a class="nav-link" href="/auth/login">' in rv
        assert b'footer' in rv
        assert b'<a href="/contact">' in rv
        # assert False

def test_navbar_loggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = 'exists'
        rv = c.post('/', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'navbar' in rv
        assert b'fixed-top' in rv
        assert b'<a class="navbar-brand" href="/">' in rv
        assert b'<button class="navbar-toggler" type="button" data-toggle="collapse"' in rv
        assert b'<a class="nav-link" href="/">' in rv
        assert b'<a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button"' in rv
        assert b'<a class="dropdown-item" href="/auth/profil">' in rv
        assert b'<a class="dropdown-item" href="/auth/logout">' in rv
        assert b'footer' in rv
        assert b'<a href="/contact">' in rv
        # assert False

# index "/"
def test_index(app):
    with app.test_client() as c:
        rv = c.post('/', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input autofocus id="queryInputField" name="name" placeholder=' in rv
        assert b'required type="text" value="">' in rv
        assert b'<input id="submit" name="submit" type="submit" value="">' in rv
        assert b'autocomplete(document.getElementById("queryInputField"))' in rv
        assert b'<a href="/help">' in rv    
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        print(session)
        assert session == {"user": None, "next": None}
        assert request.path == '/'
        # assert False

def test_index_used(app):
    with app.test_client() as c:
        rv = c.post('/', data={"name":"lorem"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session["user"] is None
        assert session["next"] is None
        assert "query" in session
        assert request.path == '/results'
        # assert False


# results "/results"
def test_results(app):
    with app.test_client() as c:
        rv = c.post('/results', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        # check for page elements
        assert b'<input autofocus id="queryInputField" name="name" placeholder=' in rv
        assert b'required type="text" value="&#39;- no search-&#39;">' in rv
        assert b'<input id="submit" name="submit" type="submit" value="">' in rv
        assert b'autocomplete(document.getElementById("queryInputField"))' in rv
        assert b'<a href="/help">' in rv
        assert b'<select class="form-control border-primary ml-0" id="sortForm" name="order" onchange="this.form.submit()">' in rv
        assert b'<option value="">' in rv
        assert b'<option value="desc">' in rv
        assert b'<option value="asc">' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'Total hits: 0' in rv
        assert b'In:' in rv
        assert b'<p>Search returned no results.</p>' in rv
        assert session["user"] is None
        assert session["order"] is None
        assert request.path == '/results'
        # assert False

def test_results_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/results', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'Total hits: 0' in rv
        assert b'In:' in rv
        assert b'<p>Search returned no results.</p>' in rv
        assert session["user"] is None
        assert session["order"] is None
        assert request.path == '/results'
        # assert False

def test_results_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        rv = c.post('/results', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        # check for page elements
        assert b'alert' in rv
        assert b"User key 'no user' not found, remove user from session"
        assert b'Total hits: 0' in rv
        assert b'In:' in rv
        assert b'<p>Search returned no results.</p>' in rv
        assert session["user"] is None
        assert session["order"] is None
        assert request.path == '/results'
        # assert False

def test_results_userLoggedIn(app):
    with app.test_client() as c:
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/results', data={"name": "lorem"}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        try:
            doc = collection["exists"]
            assert not b'alert' in rv
            assert b'Total hits: 3' in rv
            assert b'In:' in rv
            assert session["user"] == "exists"
            assert not "order" in session
            assert request.path == '/results'
            assert doc["lastsearch"] == ["'lorem'"]
        finally:
            doc["lastsearch"] = []
            doc.save()
        # assert False

def test_results_orderNone(app):
    with app.test_client() as c:
        rv = c.post('/results', data={"order": ""}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'Total hits: 0' in rv
        assert b'In:' in rv
        assert b'<p>Search returned no results.</p>' in rv
        assert session["user"] is None
        assert session["order"] == ""
        assert request.path == '/results'
        # assert False

def test_results_orderAsc(app):
    with app.test_client() as c:
        rv = c.post('/results', data={"order": "asc"}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'Total hits: 0' in rv
        assert b'In:' in rv
        assert b'<p>Search returned no results.</p>' in rv
        assert session["user"] is None
        assert session["order"] == "asc"
        assert request.path == '/results'
        # assert False

def test_results_orderDesc(app):
    with app.test_client() as c:
        rv = c.post('/results', data={"order": "desc"}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'Total hits: 0' in rv
        assert b'In:' in rv
        assert b'<p>Search returned no results.</p>' in rv
        assert session["user"] is None
        assert session["order"] == "desc"
        assert request.path == '/results'
        # assert False

def test_results_search(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = True
        rv = c.post('/results', data={"name": "lorem"}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'Total hits: 3' in rv
        assert b'In:' in rv
        assert b'<a href="/page/PMID121518513">' in rv
        assert b'<a href="/page/oai:arXiv.org:121518513">' in rv
        assert b'<a href="/page/121518513">' in rv
        assert b'<form action="/backwards" method="post">' in rv
        assert b'<p>1 - 3</p>' in rv
        assert b'<form action="/forwards" method="post">' in rv
        assert b'<div id="tags"' in rv
        assert b'href="/tags/ipsum" style=\'color: black\'> ipsum (3)' in rv
        assert session["user"] is None
        assert not "order" in session
        assert not session["showfulltext"]
        assert request.path == '/results'
        # assert False

def test_results_search_rest(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = True
        rv = c.post('/results', data={"name": "-lorem"}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'Total hits: 3' in rv
        assert request.path == '/results'
        # assert False

def test_results_search_condRest(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = True
        rv = c.post('/results', data={"name": "lorem -lorem"}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert b'alert' in rv
        assert b'Total hits: 3' in rv
        assert b'Found {&#39;multi_match&#39;: {&#39;query&#39;: &#39;lorem&#39;}} in condition and restriction, removed from condition.' in rv
        assert request.path == '/results'
        # assert False

def test_results_search_field(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = True
        rv = c.post('/results', data={"name": "title: lorem"}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'Total hits: 3' in rv
        assert request.path == '/results'
        # assert False

def test_results_search_field_damaged(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = True
        rv = c.post('/results', data={"name": "titel: lorem"}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert b'alert' in rv
        assert b'Total hits: 3' in rv
        assert b"Field &#39;titel&#39; not found do you mean &#39;title&#39;?" in rv
        assert request.path == '/results'
        # assert False

def test_results_search_field_wrong(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = True
        rv = c.post('/results', data={"name": "tatel: lorem"}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert b'alert' in rv
        assert b'Total hits: 3' in rv
        assert b"Field &#39;tatel&#39; not found. Field restriction removed." in rv
        assert request.path == '/results'
        # assert False


# page "/page/<id>"
def test_page(app):
    with app.test_client() as c:
        rv = c.post('/page/121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        # check for page elements
        assert b'<input autofocus id="queryInputField" name="name" placeholder=' in rv
        assert b'required type="text" value="">' in rv
        assert b'<input id="submit" name="submit" type="submit" value="">' in rv
        assert b'autocomplete(document.getElementById("queryInputField"))' in rv
        assert b'<a href="/help">' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'<h6>Lorem ipsum dolor</h6>' in rv
        assert not b'edited' in rv
        assert b'<p>by Lorem Ipsum and L\xc3\xb6rem Ip\xc3\x9f\xc3\xbcm</p>' in rv
        assert b'<b>Abstract:</b>' in rv
        assert b'<p><b>Date:</b> 2020-02-02</p>' in rv
        assert b'<input id="pdf" name="button" type="submit" value="pdf">' in rv
        assert b'<input id="fulltext" name="button" type="submit" value="show fulltext">' in rv
        assert not b'<p><b>Fulltext:</b>' in rv
        assert session == {'lastpage': '121518513', 'showfulltext': False}
        assert request.path == '/page/121518513'
        # assert False

def test_page_noAuthor(app):
    with app.test_client() as c:
        rv = c.post('/page/PMID121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'<h6>Lorem ipsum dolor sit amet, consetetur sadipscing elitr.</h6>' in rv
        assert b'<p>edited by Lorem Ipsum and Ip\xc3\x9f\xc3\xbcm L\xc3\xb6rem</p>' in rv
        assert b'<p><b>Abstract:</b> Lorem ipsum</p>' in rv
        assert b'<p><b>Year:</b> 2018</p>' in rv
        assert b'<p><b>Tags:</b><br>lorem, ipsum</p>' in rv
        assert session == {'lastpage': 'PMID121518513', 'showfulltext': False}
        assert request.path == '/page/PMID121518513'
        # assert False

def test_page_noAuthorNoEditor(app):
    with app.test_client() as c:
        rv = c.post('/page/oai:arXiv.org:121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'<h6>Lorem ipsum dolor</h6>' in rv
        assert not b'<p>by' in rv
        assert not b'<p>edited by' in rv
        assert b'<b>Abstract:</b>' in rv
        assert b'<p><b>Date:</b> 2007-05-23</p>' in rv
        assert b'<p><b>Tags:</b><br>lorem, ipsum, dolor, sit, amet, consetetur, elitr, sadipscing</p>' in rv
        assert session == {'lastpage': 'oai:arXiv.org:121518513', 'showfulltext': False}
        assert request.path == '/page/oai:arXiv.org:121518513'
        # assert False

def test_page_search(app):
    with app.test_client() as c:
        rv = c.post('/page/121518513', data={"name": "lorem"}, follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert session["lastpage"] == "121518513"
        assert not session["showfulltext"]
        assert session["user"] is None
        assert request.path == '/results'
        # assert False
        
def test_page_noLastpage(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = True
        rv = c.post('/page/121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'<h6>Lorem ipsum dolor</h6>' in rv
        assert not b'edited' in rv
        assert b'<p>by Lorem Ipsum and L\xc3\xb6rem Ip\xc3\x9f\xc3\xbcm</p>' in rv
        assert b'<b>Abstract:</b>' in rv
        assert b'<p><b>Date:</b> 2020-02-02</p>' in rv
        assert b'<input id="pdf" name="button" type="submit" value="pdf">' in rv
        assert b'<input id="fulltext" name="button" type="submit" value="show fulltext">' in rv
        assert not b'<p><b>Fulltext:</b>' in rv
        assert session == {'lastpage': '121518513', 'showfulltext': False}
        assert request.path == '/page/121518513'
        # assert False
        
def test_page_otherLastpage(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = True
            sess['lastpage'] = "other"
        rv = c.post('/page/121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'<h6>Lorem ipsum dolor</h6>' in rv
        assert not b'edited' in rv
        assert b'<p>by Lorem Ipsum and L\xc3\xb6rem Ip\xc3\x9f\xc3\xbcm</p>' in rv
        assert b'<b>Abstract:</b>' in rv
        assert b'<p><b>Date:</b> 2020-02-02</p>' in rv
        assert b'<input id="pdf" name="button" type="submit" value="pdf">' in rv
        assert b'<input id="fulltext" name="button" type="submit" value="show fulltext">' in rv
        assert not b'<p><b>Fulltext:</b>' in rv
        assert session == {'lastpage': '121518513', 'showfulltext': False}
        assert request.path == '/page/121518513'
        # assert False
        
def test_page_noPage(app):
    with app.test_client() as c:
        rv = c.post('/page/no page', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert b'navbar' in rv
        assert b'footer' in rv
        assert not b'alert' in rv
        assert b'Not Found' in rv
        assert session == {'lastpage': 'no page', 'showfulltext': False}
        assert request.path == '/page/no page'
        # assert False
        
def test_page_noArango(app):
    with app.test_client() as c:
        rv = c.post('/page/miss', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert b'navbar' in rv
        assert b'footer' in rv
        assert not b'alert' in rv
        assert b'<h6>Miss</h6>' in rv
        assert session == {'lastpage': 'miss', 'showfulltext': False}
        assert request.path == '/page/miss'
        # assert False


# forwards "/forwards"
def test_forwards(app):
    with app.test_client() as c:
        rv = c.post('/forwards', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert session == {'user': None, 'next': None}
        assert request.path == '/'
        # assert False
        
def test_forwards_successfully(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["from_hit"] = 0
            sess["to_hit"] = 10
            # for result
            sess['tags'] = []
            sess["query"] = ""
            sess["condition"] = {}
            sess["condition"]["must"] = []
            sess["condition"]["must_not"] = []
        rv = c.post('/forwards', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert session["from_hit"] == 10
        assert session["to_hit"] == 20
        assert request.path == '/results'
        # assert False


# backwards "/backwards"
def test_backwards(app):
    with app.test_client() as c:
        rv = c.post('/backwards', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert session == {'user': None, 'next': None}
        assert request.path == '/'
        # assert False
        
def test_backwards_successfully(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['from_hit'] = 10
            sess['to_hit'] = 20
            # for result
            sess['tags'] = []
            sess["query"] = ""
            sess["condition"] = {}
            sess["condition"]["must"] = []
            sess["condition"]["must_not"] = []
        rv = c.post('/backwards', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert session["from_hit"] == 0
        assert session["to_hit"] == 10
        assert request.path == '/results'
        # assert False


# pdf "/pdf/<id>"
def test_pdf(app):
    with app.test_client() as c:
        rv = c.post('/pdf/121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        # # check for page elements
        assert b'%PDF' in rv
        assert not b'navbar' in rv
        assert not b'footer' in rv

        assert not b'alert' in rv
        assert session == {}
        assert request.path == '/pdf/121518513'
        # assert False
        
def test_pdf_noPDF(app):
    with app.test_client() as c:
        rv = c.post('/pdf/no pdf', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert b'navbar' in rv
        assert b'footer' in rv
        assert not b'alert' in rv
        assert b'Not Found' in rv
        assert session == {}
        assert request.path == '/pdf/no pdf'
        # assert False


# fulltext "/fulltext/<id>"
def test_fulltext(app):
    with app.test_client() as c:
        rv = c.post('/fulltext/121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'<p><b>Fulltext:</b>' in rv
        assert session == {'lastpage': '121518513', 'showfulltext': True}
        assert request.path == '/page/121518513'
        # assert False

def test_fulltext_noLastpage(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = False
        rv = c.post('/fulltext/121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert not b'<p><b>Fulltext:</b>' in rv
        assert session == {'lastpage': '121518513', 'showfulltext': False}
        assert request.path == '/page/121518513'
        # assert False

def test_fulltext_noLastpage_show(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = True
        rv = c.post('/fulltext/121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert not b'<p><b>Fulltext:</b>' in rv
        assert session == {'lastpage': '121518513', 'showfulltext': False}
        assert request.path == '/page/121518513'
        # assert False

def test_fulltext_lastpage(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = False
            sess['lastpage'] = '121518513'
        rv = c.post('/fulltext/121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert b'<p><b>Fulltext:</b>' in rv
        assert session == {'lastpage': '121518513', 'showfulltext': True}
        assert request.path == '/page/121518513'
        # assert False

def test_fulltext_lastpage_show(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['showfulltext'] = True
            sess['lastpage'] = '121518513'
        rv = c.post('/fulltext/121518513', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert not b'<p><b>Fulltext:</b>' in rv
        assert session == {'lastpage': '121518513', 'showfulltext': False}
        assert request.path == '/page/121518513'
        # assert False


# tags "/tags/<tag>"
def test_tags(app):
    with app.test_client() as c:
        rv = c.post('/tags/lorem', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert session == {'user': None, 'next': None}
        assert request.path == '/'
        # assert False
        
def test_tags_add(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['tags'] = [
                {'name': 'ipsum', 'nr': 3, 'mark': True},
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
            sess["query"] = "tags: 'ipsum'"
            sess["condition"] = {}
            sess["condition"]["must"] = [{'terms': {'tags': ['ipsum']}}]
            # for result
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
        rv = c.post('/tags/lorem', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert session["tags"] == [
            {'name': 'ipsum', 'nr': 3, 'mark': True},
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
        assert request.path == '/results'
        # assert False
        
def test_tags_remove(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['tags'] = [
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
            sess['query'] = "tags: 'lorem'"
            sess["condition"] = {}
            sess["condition"]["must"] = [{'terms': {'tags': ['lorem']}}]
            # for result
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
        rv = c.post('/tags/lorem', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
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
        assert request.path == '/results'
        # assert False
        
def test_tags_noTags(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['tags'] = []
            sess["query"] = "title: 'voluptua'"
            sess["condition"] = {}
            sess["condition"]["must"] = [{'match': {'title': 'voluptua'}}]
            # for result
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
        rv = c.post('/tags/lorem', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert session['tags'] == []
        assert request.path == '/results'
        # assert False
        
def test_tags_missingTag(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['tags'] = [
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
            sess["query"] = "tags: 'lorem'"
            sess["condition"] = {}
            sess["condition"]["must"] = [{'terms': {'tags': ['lorem']}}]
            # for result
            sess["condition"]["must_not"] = []
            sess["from_hit"] = 0
            sess["to_hit"] = 10
        rv = c.post('/tags/tempor', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert session['tags'] == [
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
        assert request.path == '/results'
        # assert False

# oldsearch "/oldsearch/<search>"
def test_oldsearch(app):
    with app.test_client() as c:
        rv = c.post('/oldsearch/lorem', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        assert not b'alert' in rv
        assert session["query"] == "'lorem'"
        assert request.path == '/results'
        # assert False

# help "/help"
# wip
def test_help(app):
    with app.test_client() as c:
        rv = c.post('/help', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        # check for page elements
        assert b'navbar' in rv
        assert b'footer' in rv
        
        assert not b'alert' in rv
        assert session == {}
        assert request.path == '/help'
        # assert False

# contact "/contact"
# wip
def test_contact(app):
    with app.test_client() as c:
        rv = c.post('/contact', follow_redirects=True).data
        print(rv)
        print(session)
        print(request.path)
        # check for page elements
        assert b'navbar' in rv
        assert b'footer' in rv
        
        assert not b'alert' in rv
        assert session == {}
        assert request.path == '/contact'
        # assert False

# autocomplete "/autocomplete"
# def test_autocomplete(app):
#     with app.test_client() as c:
#         rv = c.post('/autocomplete', follow_redirects=True).data
#         print(rv)
#         print(session)
#         print(request.path)
#         # check for page elements
#         assert b'navbar' in rv
#         assert b'footer' in rv
#         # assert session == {}
#         # assert request.path == '/'
#         # assert False

# citations "/citations"
# def test_citations(app):
#     with app.test_client() as c:
#         rv = c.post('/citations', follow_redirects=True).data
#         print(rv)
#         print(session)
#         print(request.path)
#         # check for page elements
#         assert b'navbar' in rv
#         assert b'footer' in rv
#         # assert session == {}
#         # assert request.path == '/'
#         # assert False

# citation_key "/citation/<key>"
# def test_citation_key(app):
#     with app.test_client() as c:
#         rv = c.post('/citation/<key>', follow_redirects=True).data
#         print(rv)
#         print(session)
#         print(request.path)
#         # check for page elements
#         assert b'navbar' in rv
#         assert b'footer' in rv
#         # assert session == {}
#         # assert request.path == '/'
#         # assert False