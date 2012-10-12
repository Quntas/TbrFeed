#!/virtual/azyobuzin/local/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

import session
from tbrfeed import *

with session.Session() as sess:
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
