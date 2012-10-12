#!/virtual/azyobuzin/local/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

import MySQLdb

import session
from tbrfeed import *

with session.Session() as sess:
    db = MySQLdb.connect(user = dbName, passwd = dbPassword, db = dbName, charset = "utf8")
    c = db.cursor()

    c.execute("DELETE FROM %s WHERE id = %s"
        % (usersTable, db.literal(sess.data["user"][0]))
    )

    db.commit()
    c.close()
    db.close()

    del sess.data["user"]

    print "Status: 303 See Other"
    print sess.cookie
    print "Location: " + location
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
