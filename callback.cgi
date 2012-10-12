#!/virtual/azyobuzin/local/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

import hashlib
import json
import os
import random
import time
import urlparse

import MySQLdb
import oauth2

import session
from tbrfeed import *

with session.Session() as sess:
    query = dict(urlparse.parse_qsl(os.environ.get("QUERY_STRING", "")))

    if "oauth_token" in query and "oauth_verifier" in query:
        oauthToken = query["oauth_token"]
        oauthVerifier = query["oauth_verifier"]

        token = oauth2.Token(oauthToken, sess.data["request_secret"])
        token.set_verifier(oauthVerifier)

        client = oauth2.Client(oauthConsumer, token)
    	resp, content = client.request("http://www.tumblr.com/oauth/access_token", "POST")
    	accessToken = dict(urlparse.parse_qsl(content))

        del sess.data["request_secret"]

        oauthToken = accessToken["oauth_token"]
    	oauthTokenSecret = accessToken["oauth_token_secret"]

    	client = oauth2.Client(oauthConsumer, oauth2.Token(oauthToken, oauthTokenSecret))
    	resp, content = client.request("http://api.tumblr.com/v2/user/info", "POST")

    	username = json.loads(content)["response"]["user"]["name"]
        id = hashlib.sha1(username + str(time.time()) + str(random.randint(0, 99999))).hexdigest()

        db = MySQLdb.connect(user = dbName, passwd = dbPassword, db = dbName, charset = "utf8")
        c = db.cursor()

        c.execute("INSERT INTO %s (id, username, token, secret, created, lastaccess) VALUES (%s, %s, %s, %s, NOW(), NOW()) ON DUPLICATE KEY UPDATE token = %s, secret = %s, created = NOW(), lastaccess = NOW()"
            % (usersTable, db.literal(id), db.literal(username), db.literal(oauthToken), db.literal(oauthTokenSecret), db.literal(oauthToken), db.literal(oauthTokenSecret)))

        db.commit()

        c.execute("SELECT id FROM %s WHERE username = %s" % (usersTable, db.literal(username)))
        sqlResult = c.fetchone()
        id = sqlResult[0]

        c.close()
        db.close()

        sess.data["user"] = (id, username)

    print sess.cookie
    print("Location: " + location)
    print "Content-Type: text/html; charset=utf-8"
    print """
<!DOCTYPE html>
<html>
    <head>
        <meta name="robots" content="noindex">
        <title>TbrFeed</title>
    </head>
    <body>
        <p><a href="%s">Back to TbrFeed</a></p>
    </body>
</html>
""" % location
