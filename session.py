# -*- coding: utf-8 -*-

import Cookie
import datetime
import hashlib
import os
import random
import shelve
import time

class Session:
    def __init__(self):
        self.cookie = Cookie.SimpleCookie(os.environ.get('HTTP_COOKIE', ''))

        if "sid" in self.cookie:
            self.sid = self.cookie["sid"].value
        else:
            self.sid = hashlib.sha1(str(time.time()) + str(random.randint(0, 99999))).hexdigest()

        self.cookie["sid"] = self.sid

        self.data = shelve.open("./session/" + self.sid + ".pickle", writeback = True)

        self.data["expires"] = datetime.datetime.now() + datetime.timedelta(weeks = 4)
        self.cookie["sid"]["expires"] = self.data["expires"].strftime("%a, %d-%b-%Y %H:%M:%S GMT")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.data.close()
