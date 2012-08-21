#!/virtual/azyobuzin/local/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

import tbrfeed
import oauth2
import urlparse
import MySQLdb

client = oauth2.Client(tbrfeed.oauthConsumer)
resp, content = client.request("http://www.tumblr.com/oauth/request_token", "POST")
token = dict(urlparse.parse_qsl(content))

db = MySQLdb.connect(user=tbrfeed.dbName, passwd=tbrfeed.dbPassword, db=tbrfeed.dbName, charset="utf8")
c = db.cursor()

c.execute("INSERT INTO %s(oauth_token, oauth_token_secret, created) VALUES(%s, %s, now())"
	% (tbrfeed.requestSessionTable, db.literal(token["oauth_token"]), db.literal(token["oauth_token_secret"]))
)

db.commit()
c.close()
db.close()

print("Location: http://www.tumblr.com/oauth/authorize?oauth_token=" + token["oauth_token"])
print
