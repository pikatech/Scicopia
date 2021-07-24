import pytest
import os
from flask import current_app, g, session, request
from werkzeug.security import generate_password_hash

from scicopia.tests.data.initFlaskData import main as init
init()#user=True
import scicopia.app.db as db
from scicopia.app import create_app
from scicopia.app.main import main

@pytest.fixture
def app():
    app = create_app('testing')
    yield app

@main.route("/getToken/<id>", methods=["GET", "POST"])
def get_Token(id):
    token = db.generate_confirmation_token(id)
    return token

def test_login(app):
    with app.test_client() as c:
        rv = c.post('/auth/login', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="user" name="user" required type="text" value="">' in rv
        assert b'input class="form-control is-invalid" id="password" name="password" required type="password" value=""' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'<a href="/auth/register">' in rv
        assert b'<a href="/auth/reset">' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"next": None}
        assert request.path == '/auth/login'

def test_login_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/auth/login', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="user" name="user" required type="text" value="">' in rv
        assert b'input class="form-control is-invalid" id="password" name="password" required type="password" value=""' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'<a href="/auth/register">' in rv
        assert b'<a href="/auth/reset">' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"next": None, "user": None}
        assert request.path == '/auth/login'

def test_login_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        rv = c.post('/auth/login', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="user" name="user" required type="text" value="">' in rv
        assert b'input class="form-control is-invalid" id="password" name="password" required type="password" value=""' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'<a href="/auth/register">' in rv
        assert b'<a href="/auth/reset">' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"next": None, "user": 'no user'}
        assert request.path == '/auth/login'

def test_login_userLoggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/login', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="user" name="user" required type="text" value="">' in rv
        assert b'input class="form-control is-invalid" id="password" name="password" required type="password" value=""' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'<a href="/auth/register">' in rv
        assert b'<a href="/auth/reset">' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"next": None, "user": "exists"}
        assert request.path == '/auth/login'
        # assert False

def test_login_successfully_unconfirmed(app):
    with app.test_client() as c:
        rv = c.post('/auth/login', data={"user": "Test", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert not b'This field is required.' in rv
        print(session)
        assert session == {"next": None, "user": "exists"}
        assert request.path == '/auth/unconfirmed'

def test_login_successfully_confirmed(app):
    with app.test_client() as c:
        rv = c.post('/auth/login', data={"user": "Test2", "password": "test2"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert not b'This field is required.' in rv
        print(session)
        assert session == {"next": None, "user": "exists2"}
        assert request.path == '/'

def test_login_successfully_unconfirmed_next(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["next"] = '/auth/profil'
        rv = c.post('/auth/login', data={"user": "Test", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert not b'This field is required.' in rv
        print(session)
        assert session == {"next": None, "user": "exists"}
        assert request.path == '/auth/profil'

def test_login_successfully_confirmed_next(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["next"] = '/auth/profil'
        rv = c.post('/auth/login', data={"user": "Test2", "password": "test2"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert not b'This field is required.' in rv
        print(session)
        assert session == {"next": None, "user": "exists2"}
        assert request.path == '/auth/profil'

def test_login_successfully_unconfirmed_nextNoLink(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["next"] = 'auth/profil'
        rv = c.post('/auth/login', data={"user": "Test", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert not b'This field is required.' in rv
        print(session)
        assert session == {"next": None, "user": "exists"}
        assert request.path == '/auth/unconfirmed'

def test_login_successfully_confirmed_nextNoLink(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["next"] = 'auth/profil'
        rv = c.post('/auth/login', data={"user": "Test2", "password": "test2"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert not b'This field is required.' in rv
        print(session)
        assert session == {"next": None, "user": "exists2"}
        assert request.path == '/'

def test_login_wrong_password(app):
    with app.test_client() as c:
        rv = c.post('/auth/login', data={"user": "Test", "password": "wrong password"}, follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'Invalid username or password.' in rv
        assert not b'This field is required.' in rv
        print(session)
        assert session == {"next": None}
        assert request.path == '/auth/login'

def test_login_wrong_user(app):
    with app.test_client() as c:
        rv = c.post('/auth/login', data={"user": "no user", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'Invalid username or password.' in rv
        assert not b'This field is required.' in rv
        print(session)
        assert session == {"next": None}
        assert request.path == '/auth/login'

def test_login_no_password(app):
    with app.test_client() as c:
        rv = c.post('/auth/login', data={"user": "Test", "password": ""}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"next": None}
        assert request.path == '/auth/login'

def test_login_noUser(app):
    with app.test_client() as c:
        rv = c.post('/auth/login', data={"user": "", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"next": None}
        assert request.path == '/auth/login'
        

def test_register(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="username" name="username" required type="text" value="">' in rv
        assert b'<input class="form-control is-invalid" id="email" name="email" required type="text" value="">' in rv
        assert b'<input class="form-control is-invalid" id="password" name="password" required type="password" value="">' in rv
        assert b'<input class="form-control is-invalid" id="password2" name="password2" required type="password" value="">' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/auth/register', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="username" name="username" required type="text" value="">' in rv
        assert b'<input class="form-control is-invalid" id="email" name="email" required type="text" value="">' in rv
        assert b'<input class="form-control is-invalid" id="password" name="password" required type="password" value="">' in rv
        assert b'<input class="form-control is-invalid" id="password2" name="password2" required type="password" value="">' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": None}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        rv = c.post('/auth/register', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="username" name="username" required type="text" value="">' in rv
        assert b'<input class="form-control is-invalid" id="email" name="email" required type="text" value="">' in rv
        assert b'<input class="form-control is-invalid" id="password" name="password" required type="password" value="">' in rv
        assert b'<input class="form-control is-invalid" id="password2" name="password2" required type="password" value="">' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "no user"}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_userLoggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/register', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="username" name="username" required type="text" value="">' in rv
        assert b'<input class="form-control is-invalid" id="email" name="email" required type="text" value="">' in rv
        assert b'<input class="form-control is-invalid" id="password" name="password" required type="password" value="">' in rv
        assert b'<input class="form-control is-invalid" id="password2" name="password2" required type="password" value="">' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_successfully(app):        
    with app.test_client() as c:
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
            collectionname = current_app.config["USERCOLLECTIONNAME"]
        rv = c.post('/auth/register', data={"username": "Test3", "email": "test3@email.de", "password": "test", "password2": "test"}, follow_redirects=True).data
        print(rv)
        try:
            assert b'alert' in rv
            assert b'A confirmation email has been sent to you by email.' in rv
            print(session)
            assert session == {"next": None}
            print(request.path)
            assert request.path == '/auth/login'
        finally:
            aql = f"FOR x IN {collectionname} FILTER x.username == 'Test3' RETURN x._key"
            user = current_app.config["DB"].AQLQuery(
                aql, rawResults=True, batchSize=1
            )
            assert user
            doc = collection[user[0]]
            doc.delete()
            aql = f"FOR x IN {collectionname} FILTER x.username == 'Test3' RETURN x._key"
            user = current_app.config["DB"].AQLQuery(
                aql, rawResults=True, batchSize=1
            )
            assert not user
        # assert False

def test_register_successfully_userLoggedIn(app):        
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
            collectionname = current_app.config["USERCOLLECTIONNAME"]
        rv = c.post('/auth/register', data={"username": "Test4", "email": "test4@email.de", "password": "test", "password2": "test"}, follow_redirects=True).data
        print(rv)
        try:
            assert b'alert' in rv
            assert b'A confirmation email has been sent to you by email.' in rv
            print(session)
            assert session == {"next": None, "user": "exists"}
            print(request.path)
            assert request.path == '/auth/login'
        finally:
            aql = f"FOR x IN {collectionname} FILTER x.username == 'Test4' RETURN x._key"
            user = current_app.config["DB"].AQLQuery(
                aql, rawResults=True, batchSize=1
            )
            assert user
            doc = collection[user[0]]
            doc.delete()
            aql = f"FOR x IN {collectionname} FILTER x.username == 'Test4' RETURN x._key"
            user = current_app.config["DB"].AQLQuery(
                aql, rawResults=True, batchSize=1
            )
            assert not user
        # assert False

def test_register_no_user(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', data={"username": "", "email": "test3@email.de", "password": "test", "password2": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_no_email(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', data={"username": "Test3", "email": "", "password": "test", "password2": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_no_password(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', data={"username": "Test3", "email": "test3@email.de", "password": "", "password2": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_no_passwor2(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', data={"username": "Test", "email": "test3@email.de", "password": "test", "password2": ""}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_existing_user(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', data={"username": "Test", "email": "test3@email.de", "password": "test", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Username already in use.' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_existing_email(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', data={"username": "Test3", "email": "test@email.de", "password": "test", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Email already registered.' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_different_password(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', data={"username": "Test3", "email": "test3@email.de", "password": "test", "password": "test2"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Passwords must match.' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_wrong_user_format(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', data={"username": "Test!", "email": "test3@email.de", "password": "test", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Usernames must have only letters, numbers, dots or underscores' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_wrong_user_format2(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', data={"username": "0Test", "email": "test3@email.de", "password": "test", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Usernames must have only letters, numbers, dots or underscores' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False

def test_register_wrong_email_format(app):
    with app.test_client() as c:
        rv = c.post('/auth/register', data={"username": "Test3", "email": "test", "password": "test", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Invalid email address.' in rv
        print(session)
        assert session == {}
        print(request.path)
        assert request.path == '/auth/register'
        # assert False
        

def test_logout(app):
    with app.test_client() as c:
        rv = c.post('/auth/logout', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": None, "user": None}
        print(request.path)
        assert request.path == '/'
        # assert False

def test_logout_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/auth/logout', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": None, "user": None}
        print(request.path)
        assert request.path == '/'
        # assert False

def test_logout_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        rv = c.post('/auth/logout', follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'You have been logged out.' in rv
        print(session)
        assert session == {"next": None, "user": None}
        print(request.path)
        assert request.path == '/'
        # assert False

def test_logout_userLoggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/logout', follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'You have been logged out.' in rv
        print(session)
        assert session == {"next": None, "user": None}
        print(request.path)
        assert request.path == '/'
        # assert False
        

def test_profil(app):
    with app.test_client() as c:
        rv = c.post('/auth/profil', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/profil', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_profil_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/auth/profil', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/profil', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_profil_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = 'no user'
        rv = c.post('/auth/profil', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/profil', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_profil_userLoggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/profil', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<a href="/auth/change-password">' in rv
        assert b'<a href="/auth/change_username">' in rv
        assert b'<a href="/auth/change_email">' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'No Search recorded' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/profil'
        # assert False

def test_profil_userLoggedIn_search(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists2"
        rv = c.post('/auth/profil', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'<p><b>Last Search:</b><br>\n      \n    \n    <li><a href="/oldsearch/Ipsum">Ipsum</a></li></p>\n    \n    <li><a href="/oldsearch/ipsum">ipsum</a></li></p>\n    \n    <li><a href="/oldsearch/loreM">loreM</a></li></p>\n    \n    <li><a href="/oldsearch/lorem">lorem</a></li></p>\n    \n    <li><a href="/oldsearch/Lorem">Lorem</a></li></p>' in rv
        print(session)
        assert session == {"user": "exists2"}
        print(request.path)
        assert request.path == '/auth/profil'
        # assert False
        

def test_change_password_request(app):
    with app.test_client() as c:
        rv = c.post('/auth/change-password', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/change-password', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_change_password_request_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/auth/change-password', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/change-password', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_change_password_request_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        rv = c.post('/auth/change-password', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/change-password', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_change_password_request_userloggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change-password', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="old_password" name="old_password" required type="password" value="">' in rv
        assert b'input class="form-control is-invalid" id="password" name="password" required type="password" value=""' in rv
        assert b'input class="form-control is-invalid" id="password2" name="password2" required type="password" value=""' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change-password'
        # assert False

def test_change_password_request_successfully(app):
    with app.test_client() as c:
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change-password', data={"old_password": "test", "password": "test2", "password2": "test2"}, follow_redirects=True).data
        print(rv)
        try:
            doc = collection["exists"]
            assert b'alert' in rv
            assert b'Your password has been updated.' in rv
            print(session)
            assert session == {"next": None, "user": "exists"}
            print(request.path)
            assert request.path == '/'
        finally:
            doc["password_hash"] = generate_password_hash("test")
            doc.save()
        # assert False

def test_change_password_request_no_oldPassword(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change-password', data={"old_password": "", "password": "test2", "password2": "test2"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change-password'
        # assert False

def test_change_password_request_no_password(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change-password', data={"old_password": "test", "password": "", "password2": "test2"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change-password'
        # assert False

def test_change_password_request_no_password2(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change-password', data={"old_password": "test", "password": "test2", "password2": ""}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change-password'
        # assert False

def test_change_password_request_wrong_oldPassword(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change-password', data={"old_password": "test2", "password": "test", "password2": "test"}, follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'Invalid password.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change-password'
        # assert False

def test_change_password_request_different_password(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change-password', data={"old_password": "test", "password": "test", "password2": "test2"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Passwords must match.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change-password'
        # assert False

def test_change_password_request_new_password_same_old(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change-password', data={"old_password": "test", "password": "test", "password2": "test"}, follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'Your password has been updated.' in rv
        print(session)
        assert session == {"next": None, "user": "exists"}
        print(request.path)
        assert request.path == '/'
        # assert False
        

def test_password_reset_request(app):
    with app.test_client() as c:
        rv = c.post('/auth/reset', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="email" name="email" required type="text" value="">' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": None}
        print(request.path)
        assert request.path == '/auth/reset'
        # assert False

def test_password_reset_request_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/auth/reset', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="email" name="email" required type="text" value="">' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": None}
        print(request.path)
        assert request.path == '/auth/reset'
        # assert False

def test_password_reset_request_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        rv = c.post('/auth/reset', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": None, "user": "no user"}
        print(request.path)
        assert request.path == '/'
        # assert False

def test_password_reset_request_userLoggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/reset', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": None, "user": "exists"}
        print(request.path)
        assert request.path == '/'
        # assert False

def test_password_reset_request_successfully(app):
    with app.test_client() as c:
        rv = c.post('/auth/reset', data={"email": "test@email.de"}, follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'An email with instructions to reset your password has been sent to you.' in rv
        print(session)
        assert session == {"next": None, "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_password_reset_request_no_data(app):
    with app.test_client() as c:
        rv = c.post('/auth/reset', data={"email": "lorem@email.de"}, follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'No data found, please contact the serveradmin to reset your password.' in rv
        print(session)
        assert session == {"user": None}
        print(request.path)
        assert request.path == '/auth/reset'
        # assert False

def test_password_reset_request_wrong_format(app):
    with app.test_client() as c:
        rv = c.post('/auth/reset', data={"email": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Invalid email address.' in rv
        print(session)
        assert session == {"user": None}
        print(request.path)
        assert request.path == '/auth/reset'
        # assert False
        

def test_password_reset(app):
    with app.test_client() as c:
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/reset/{token}', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'input class="form-control is-invalid" id="password" name="password" required type="password" value=""' in rv
        assert b'input class="form-control is-invalid" id="password2" name="password2" required type="password" value=""' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": None}
        print(request.path)
        assert request.path == f'/auth/reset/{token}'
        # assert False

def test_password_reset_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/reset/{token}', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'input class="form-control is-invalid" id="password" name="password" required type="password" value=""' in rv
        assert b'input class="form-control is-invalid" id="password2" name="password2" required type="password" value=""' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": None}
        print(request.path)
        assert request.path == f'/auth/reset/{token}'
        # assert False

def test_password_reset_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        token = c.post('/getToken/no user', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/reset/{token}', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": None, "user": "no user"}
        print(request.path)
        assert request.path == '/'
        # assert False

def test_password_reset_userLoggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/reset/{token}', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": None, "user": "exists"}
        print(request.path)
        assert request.path == '/'
        # assert False

def test_password_reset_successfully(app):
    with app.test_client() as c:
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/reset/{token}', data={"password": "test", "password2": "test"}, follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'Your password has been updated.' in rv
        print(session)
        assert session == {"next": None, "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_password_reset_wrong_token(app):
    with app.test_client() as c:
        rv = c.post(f'/auth/reset/no token', data={"password": "test", "password2": "test"}, follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'The confirmation link is invalid or has expired.' in rv
        print(session)
        assert session == {"next": None, "user": None}
        print(request.path)
        assert request.path == '/'
        # assert False

def test_password_reset_no_password(app):
    with app.test_client() as c:
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/reset/{token}', data={"password": "", "password2": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": None}
        print(request.path)
        assert request.path == f'/auth/reset/{token}'
        # assert False

def test_password_reset_no_password2(app):
    with app.test_client() as c:
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/reset/{token}', data={"password": "test", "password2": ""}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": None}
        print(request.path)
        assert request.path == f'/auth/reset/{token}'
        # assert False
        

def test_change_username_request(app):
    with app.test_client() as c:
        rv = c.post('/auth/change_username', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/change_username', "user": None}
        print(request.path)
        assert request.path == '/auth/login'

def test_change_username_request_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/auth/change_username', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/change_username', "user": None}
        print(request.path)
        assert request.path == '/auth/login'

def test_change_username_request_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        rv = c.post('/auth/change_username', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/change_username', "user": None}
        print(request.path)
        assert request.path == '/auth/login'

def test_change_username_request_userloggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_username', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="username" name="username" required type="text" value="">' in rv
        assert b'input class="form-control is-invalid" id="password" name="password" required type="password" value=""' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_username'
        # assert False

def test_change_username_request_successfully(app):
    with app.test_client() as c:
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_username', data={"username": "New", "password": "test"}, follow_redirects=True).data
        print(rv)
        try:
            doc = collection["exists"]
            assert b'alert' in rv
            assert b'Your username has been updated.' in rv
            print(session)
            assert session == {"next": None, "user": "exists"}
            print(request.path)
            assert request.path == '/'
            assert doc["username"] == "New"
        finally:
            doc["username"] = "Test"
            doc.save()
        # assert False

def test_change_username_request_no_user(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_username', data={"username": "", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_username'
        # assert False

def test_change_username_request_no_password(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_username', data={"username": "New", "password": ""}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_username'
        # assert False

def test_change_username_request_wrong_password(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_username', data={"username": "New", "password": "test2"}, follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'Invalid password.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_username'
        # assert False

def test_change_username_request_existing_user(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_username', data={"username": "Test", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Username already in use.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_username'
        # assert False
        

def test_change_email_request(app):
    with app.test_client() as c:
        rv = c.post('/auth/change_email', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/change_email', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_change_email_request_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/auth/change_email', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/change_email', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_change_email_request_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        rv = c.post('/auth/change_email', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/change_email', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_change_email_request_userLoggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_email', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'<input class="form-control is-invalid" id="email" name="email" required type="text" value="">' in rv
        assert b'input class="form-control is-invalid" id="password" name="password" required type="password" value=""' in rv
        assert b'<input class="btn btn-primary" id="submit" name="submit" type="submit" value=' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_email'
        # assert False

def test_change_email_request_successfully(app):
    with app.test_client() as c:
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
        with c.session_transaction() as sess:
            sess['user'] = "exists2"
        rv = c.post('/auth/change_email', data={"email": "new@email.de", "password": "test2"}, follow_redirects=True).data
        print(rv)
        try:
            doc = collection["exists2"]
            assert b'alert' in rv
            assert b'Your email adress has been updated.' in rv
            assert b'An email with instructions to confirm your new email address has been sent to you.' in rv
            print(session)
            assert session == {"next": None, "user": "exists2"}
            print(request.path)
            assert request.path == '/'
            assert doc["email"] == "new@email.de"
            assert not doc["confirmed"]
        finally:
            doc["email"] = "test2@email.de"
            doc["confirmed"] = True
            doc.save()
        # assert False

def test_change_email_request_no_email(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_email', data={"email": "", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_email'
        # assert False

def test_change_email_request_no_password(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_email', data={"email": "new@email.de", "password": ""}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'This field is required.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_email'
        # assert False

def test_change_email_request_wrong_email_format(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_email', data={"email": "new", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Invalid email address.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_email'
        # assert False

def test_change_email_request_wrong_password(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_email', data={"email": "new@email.de", "password": "test2"}, follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'Invalid password.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_email'
        # assert False

def test_change_email_request_existing_email(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/change_email', data={"email": "test@email.de", "password": "test"}, follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        assert b'Email already registered.' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/change_email'
        # assert False
        

def test_change_email(app):
    with app.test_client() as c:
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/change_email/{token}', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": f'/auth/change_email/{token}', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_change_email_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/change_email/{token}', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": f'/auth/change_email/{token}', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_change_email_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        token = c.post('/getToken/no user', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/change_email/{token}', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": f'/auth/change_email/{token}', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_change_email_userLoggedIn(app):
    with app.test_client() as c:
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/change_email/{token}', follow_redirects=True).data
        print(rv)
        try:
            doc = collection["exists"]
            assert b'alert' in rv
            assert b'Your new email address has been confirmed.' in rv
            print(session)
            assert session == {"next": None, "user": "exists"}
            print(request.path)
            assert request.path == '/'
            print(doc["confirmed"])
            assert doc["confirmed"]
        finally:
            doc["confirmed"] = False
            doc.save()
        # assert False

def test_change_email_confirmed(app):
    with app.test_client() as c:
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
        with c.session_transaction() as sess:
            sess['user'] = "exists2"
        token = c.post('/getToken/exists2', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/change_email/{token}', follow_redirects=True).data
        print(rv)
        try:
            doc = collection["exists2"]
            assert not b'alert' in rv
            print(session)
            assert session == {"next": None, "user": "exists2"}
            print(request.path)
            assert request.path == '/'
            print(doc["confirmed"])
            assert doc["confirmed"]
        finally:
            doc["confirmed"] = True
            doc.save()
        # assert False

def test_change_email_no_token(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        token = c.post('/getToken/no token', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/change_email/{token}', follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'The confirmation link is invalid or has expired.' in rv
        print(session)
        assert session == {"next": None, "user": "exists"}
        print(request.path)
        assert request.path == '/'
        # assert False
        

def test_unconfirmed(app):
    with app.test_client() as c:
        rv = c.post('/auth/unconfirmed', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": None, "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_unconfirmed_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/auth/unconfirmed', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": None, "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_unconfirmed_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        rv = c.post('/auth/unconfirmed', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": None, "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_unconfirmed_userLoggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/unconfirmed', follow_redirects=True).data
        print(rv)
        # check for page elements
        assert b'Hello, Test!' in rv
        assert b'<h3>You have not confirmed your email adress yet.</h3>' in rv
        assert b'To verify we have stored your email adress correctly you should confirm it.' in rv
        assert b'Check your inbox, you should have received an email with a confirmation link.' in rv
        assert b'<a href="/auth/confirm">' in rv
        assert b'navbar' in rv
        assert b'footer' in rv

        assert not b'alert' in rv
        print(session)
        assert session == {"user": "exists"}
        print(request.path)
        assert request.path == '/auth/unconfirmed'
        # assert False
        

def test_resend_confirmation(app):
    with app.test_client() as c:
        rv = c.post('/auth/confirm', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/confirm', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_resend_confirmation_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        rv = c.post('/auth/confirm', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/confirm', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_resend_confirmation_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        rv = c.post('/auth/confirm', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": '/auth/confirm', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_resend_confirmation_userLoggedIn(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        rv = c.post('/auth/confirm', follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'A new confirmation email has been sent to you by email.' in rv
        print(session)
        assert session == {"next": None, "user": "exists"}
        print(request.path)
        assert request.path == '/'
        # assert False
        

def test_confirm(app):
    with app.test_client() as c:
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/confirm/{token}', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": f'/auth/confirm/{token}', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_confirm_userNone(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = None
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/confirm/{token}', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": f'/auth/confirm/{token}', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_confirm_userNoUser(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "no user"
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/confirm/{token}', follow_redirects=True).data
        print(rv)
        assert not b'alert' in rv
        print(session)
        assert session == {"next": f'/auth/confirm/{token}', "user": None}
        print(request.path)
        assert request.path == '/auth/login'
        # assert False

def test_confirm_userLoggedIn(app):
    with app.test_client() as c:
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        token = c.post('/getToken/exists', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/confirm/{token}', follow_redirects=True).data
        print(rv)
        try:
            doc = collection["exists"]
            assert b'alert' in rv
            assert b'You have confirmed your account. Thanks!' in rv
            print(session)
            assert session == {"next": None, "user": "exists"}
            print(request.path)
            assert request.path == '/'
            print(doc["confirmed"])
            assert doc["confirmed"]
        finally:
            doc["confirmed"] = False
            doc.save()
        # assert False

def test_confirm_confirmed(app):
    with app.test_client() as c:
        with app.app_context():
            collection = current_app.config["USERCOLLECTION"]
        with c.session_transaction() as sess:
            sess['user'] = "exists2"
        token = c.post('/getToken/exists2', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/confirm/{token}', follow_redirects=True).data
        print(rv)
        try:
            doc = collection["exists2"]
            assert not b'alert' in rv
            print(session)
            assert session == {"next": None, "user": "exists2"}
            print(request.path)
            assert request.path == '/'
            print(doc["confirmed"])
            assert doc["confirmed"]
        finally:
            doc["confirmed"] = True
            doc.save()
        # assert False

def test_confirm_no_token(app):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user'] = "exists"
        token = c.post('/getToken/no token', follow_redirects=True).data.decode("utf-8")
        rv = c.post(f'/auth/confirm/{token}', follow_redirects=True).data
        print(rv)
        assert b'alert' in rv
        assert b'The confirmation link is invalid or has expired.' in rv
        print(session)
        assert session == {"next": None, "user": "exists"}
        print(request.path)
        assert request.path == '/'
        # assert False
