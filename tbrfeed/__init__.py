# -*- coding: Shift_JIS -*-

import os
import flask
import jinja2

app = flask.Flask(__name__)
app.jinja_loader = jinja2.FileSystemLoader(["tbrfeed/templates"])
app.secret_key = os.environ.get("TBRFEED_SECRET_KEY")
app.debug = True

@app.before_request
def before_request():
    flask.session.permanent = True

import hashlib
import random
import time

from tbrfeed import database, feedgen
import tumblr

def tumblr_client(oauth_token=None, oauth_token_secret=None):
    return tumblr.Tumblr(
        os.environ.get("TBRFEED_CONSUMER_KEY"),
        os.environ.get("TBRFEED_CONSUMER_SECRET"),
        oauth_token, oauth_token_secret)

def create_hash():
    return hashlib.sha1((username + str(time.time()) + str(random.randint(0, 99999))).encode("utf-8")).hexdigest()

def csrf_protect():
    token = flask.session.pop("_csrf_token", None)
    if not token or token != flask.request.args.get("csrf_token"):
        abort(400)

@app.route("/")
def index():
    csrf_token = create_hash()
    flask.session["_csrf_token"] = create_hash()
    return flask.render_template("loggedin.html" if "user_id" in flask.session else "unlogin.html", csrf_token=csrf_token)

@app.route("/authorize")
def authorize():
    csrf_protect()
    client = tumblr_client()
    client.request_token("http://%s/callback" % flask.request.headers.get("Host"))
    flask.session["request_secret"] = client.oauth_token_secret
    return flask.redirect(client.get_authorize_uri())

@app.route("/callback")
def callback():
    oauth_token = flask.request.args.get("oauth_token")
    oauth_verifier = flask.request.args.get("oauth_verifier")
    if not oauth_token or not oauth_verifier:
        flask.abort(400)
    oauth_token_secret = flask.session.get("request_secret")
    if not oauth_token_secret:
        flask.abort(403)
    del flask.session["request_secret"]

    client = tumblr_client(oauth_token, oauth_token_secret)
    client.access_token(oauth_verifier)

    info = client.user_info()
    username = info["name"]
    id = create_hash()
    
    with database.Connection() as cursor:
        cursor.execute("SELECT update_user(%s, %s, %s, %s)", (id, username, client.oauth_token, client.oauth_token_secret))
        id = cursor.fetchone()[0]

    flask.session["user_id"] = id
    flask.session["user_name"] = username

    return flask.redirect(flask.url_for("index"))

@app.route("/logout")
def logout():
    csrf_protect()
    del flask.session["user_id"]
    del flask.session["user_name"]
    return flask.redirect(flask.url_for("index"))

@app.route("/suspend")
def suspend():
    csrf_protect()
    with database.Connection() as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s", (flask.session["user_id"],))
    return logout()

def get_dashboard(id, type):
    with database.Connection() as cursor:
        cursor.execute("SELECT username, token, secret FROM users WHERE id = %s", (id,))
        result = cursor.fetchone()
        assert result
        cursor.execute("SELECT update_lastaccess(%s)", (id,))
    username, token, secret = result
    return (username, tumblr_client(token, secret).user_dashboard(type=type))

@app.route("/feed/<id>", defaults={"type": None})
@app.route("/feed/<id>.rss", defaults={"type": None})
@app.route("/feed/<id>/<type>")
@app.route("/feed/<id>/<type>.rss")
def feed_rss(id, type):
    username, posts = get_dashboard(id, type)
    return flask.Response(feedgen.generate_rss(flask.request.url, username, type, posts), mimetype="application/rss+xml")

@app.route("/feed/<id>.atom", defaults={"type": None})
@app.route("/feed/<id>/<type>.atom")
def feed_atom(id, type):
    username, posts = get_dashboard(id, type)
    return flask.Response(feedgen.generate_atom(flask.request.url, username, type, posts), mimetype="application/atom+xml")
