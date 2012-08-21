#!/virtual/azyobuzin/local/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

import tbrfeed
import os
import Cookie

sc = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE",""))
if tbrfeed.cookieKey in sc:
	sc[tbrfeed.cookieKey]["expires"] = "Tue, 1-Jan-1980 00:00:00"

print(sc.output())
print("Location: " + tbrfeed.location)
print
