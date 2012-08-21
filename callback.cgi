#!/virtual/azyobuzin/local/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

import tbrfeed
import os
import oauth2
import urlparse
import MySQLdb
import Cookie
import json
import hashlib
import datetime

query = dict(urlparse.parse_qsl(os.environ.get("QUERY_STRING", "")))

if "oauth_token" in query and "oauth_verifier" in query:
	oauthToken = query["oauth_token"]
	oauthVerifier = query["oauth_verifier"]
	
	db = MySQLdb.connect(user=tbrfeed.dbName, passwd=tbrfeed.dbPassword, db=tbrfeed.dbName, charset="utf8")
	c = db.cursor()
	
	c.execute("SELECT id, oauth_token_secret FROM %s WHERE oauth_token = %s"
		% (tbrfeed.requestSessionTable, db.literal(oauthToken))
	)
	
	sqlResult = c.fetchone()
	token = oauth2.Token(oauthToken, sqlResult[1])
	token.set_verifier(oauthVerifier)
	
	client = oauth2.Client(tbrfeed.oauthConsumer, token)
	resp, content = client.request("http://www.tumblr.com/oauth/access_token", "POST")
	accessToken = dict(urlparse.parse_qsl(content))
	
	c.execute("DELETE FROM %s WHERE id = %s"
		% (tbrfeed.requestSessionTable, sqlResult[0])
	)
	
	oauthToken = accessToken["oauth_token"]
	oauthTokenSecret = accessToken["oauth_token_secret"]
	
	client = oauth2.Client(tbrfeed.oauthConsumer, oauth2.Token(key=oauthToken, secret=oauthTokenSecret))
	resp, content = client.request("http://api.tumblr.com/v2/user/info", "POST")
	
	username = json.loads(content)["response"]["user"]["name"]
	
	digest = hashlib.sha1("TbrFeed " + username).hexdigest()
	
	c.execute("SELECT id FROM %s WHERE digest = %s"
		% (tbrfeed.usersTable, db.literal(digest)))
	
	sqlResult = c.fetchone()
	
	if sqlResult is None:
		c.execute("""
			INSERT INTO %s(digest, oauth_token, oauth_token_secret, username, created, last_access)
			VALUES(%s, %s, %s, %s, now(), now())
		""" % (tbrfeed.usersTable, db.literal(digest), db.literal(oauthToken), db.literal(oauthTokenSecret), db.literal(username)))
	else:
		c.execute("""
			UPDATE %s SET oauth_token = %s, oauth_token_secret = %s, last_access = now()
			WHERE id = %s
		""" % (tbrfeed.usersTable, db.literal(oauthToken), db.literal(oauthTokenSecret), sqlResult[0]))
	
	db.commit()
	c.close()
	db.close()
	
	sc = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE",""))
	sc[tbrfeed.cookieKey] = digest
 	sc[tbrfeed.cookieKey]["expires"] = (datetime.datetime.now() + datetime.timedelta(weeks=4)).strftime("%a, %d-%b-%Y %H:%M:%S GMT")
	
	print(sc.output())

print("Location: " + tbrfeed.location)
print
