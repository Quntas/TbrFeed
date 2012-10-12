#!/virtual/azyobuzin/local/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

import urlparse

import oauth2

import session
from tbrfeed import *

with session.Session() as sess:
    client = oauth2.Client(oauthConsumer)
    resp, content = client.request("http://www.tumblr.com/oauth/request_token", "POST")
    token = dict(urlparse.parse_qsl(content))

    sess.data["request_secret"] = token["oauth_token_secret"]

    uri = "http://www.tumblr.com/oauth/authorize?oauth_token=" + token["oauth_token"]

    print "Status: 303 See Other"
    print sess.cookie
    print "Location: " + uri
    print "Content-Type: text/html; charset=utf-8"
    print """
<!DOCTYPE html>
<html>
    <head>
        <meta name="robots" content="noindex">
        <title>TbrFeed</title>
    </head>
    <body>
        <p><a href="%s">Login in with Tumblr</a></p>
    </body>
</html>
""" % uri
