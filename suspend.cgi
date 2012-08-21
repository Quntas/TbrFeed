#!/virtual/azyobuzin/local/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

import tbrfeed
import os
import cgi
import MySQLdb
import urlparse

form = cgi.FieldStorage()

if form.has_key("id"):
	db = MySQLdb.connect(user=tbrfeed.dbName, passwd=tbrfeed.dbPassword, db=tbrfeed.dbName, charset="utf8")
	c = db.cursor()
	
	c.execute("DELETE FROM %s WHERE digest = %s"
		% (tbrfeed.usersTable, db.literal(form["id"].value))
	)
	
	db.commit()
	c.close()
	db.close()

print("Location: " + tbrfeed.location)
print
