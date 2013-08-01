# -*- coding: Shift_JIS -*-

import flask
import jinja2

app = flask.Flask(__name__)
app.jinja_loader = jinja2.FileSystemLoader(["tbrfeed/templates"])
app.secret_key = "{FA5C00CF-BC7A-45CC-8BFD-FB8C99A68600}"
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
        "kQoBI75Uz8eWfmHSDVPNHWXu98I26Zg0q0jI8WvuZ52y68ZCYx",
        "3lDXj8P4C5UM6MP3b8HyWt7gY26Fu4vFKiBovoZl0Kjfp1Wixc",
        oauth_token, oauth_token_secret)

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/authorize")
def authorize():
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

    client = tumblr_client(oauth_token, oauth_token_secret)
    client.access_token(oauth_verifier)

    info = client.user_info()
    username = info["name"]
    id = hashlib.sha1((username + str(time.time()) + str(random.randint(0, 99999))).encode("utf-8")).hexdigest()
    
    with database.Connection() as cursor:
        cursor.execute("SELECT update_user(%s, %s, %s, %s)", (id, username, client.oauth_token, client.oauth_token_secret))
        id = cursor.fetchone()[0]

    flask.session["user_id"] = id
    flask.session["user_name"] = username

    return flask.redirect(flask.url_for("index"))

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
    return flask.Response(feedgen.generate_rss(username, type, posts), mimetype="application/rss+xml")
