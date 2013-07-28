# -*- coding: Shift_JIS -*-

from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return """<!DOCTYPE html>
<html>
<meta charset="utf-8">
<title>TbrFeed</title>
<h1>テストなう</h1>
</html>
"""
