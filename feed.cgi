#!/virtual/azyobuzin/local/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

import json
import os
import sys
from xml.sax.saxutils import *

from dateutil.parser import parse
import MySQLdb
import oauth2
import webhelpers.text
import webhelpers.html.converters
import webhelpers.html.tools

from tbrfeed import *

def createTitle(post):
    re = post["title"] if "title" in post and post["title"] is not None else ""
    if len(re) == 0:
        re = post["type"].capitalize()
        content = ""

        if "body" in post and post["body"] is not None and len(post["body"]) != 0:
            content = post["body"]
        elif "caption" in post and post["caption"] is not None and len(post["caption"]) != 0:
            content = post["caption"]
        elif "text" in post and post["text"] is not None and len(post["text"]) != 0:
            content = post["text"]
        elif "description" in post and post["description"] is not None and len(post["description"]) != 0:
            content = post["description"]
        elif "question" in post and post["question"] is not None and len(post["question"]) != 0:
            content = post["question"]

        if len(content) != 0:
            re += ": " + webhelpers.html.tools.strip_tags(content)

        return webhelpers.text.truncate(re, 60)
    else:
        return re

def createDescription(post):
    type = post["type"]

    if type == "text":
        re = post["body"]
        if "source_url" in post:
            re += "<p><a href=%s>%s</a></p>" % (quoteattr(post["source_url"]), escape(post["source_title"]))
        return re
    elif type == "photo":
        isLink = "link_url" in post
        re = "<p>"
        if isLink:
            re += "<a href=" + quoteattr(post["link_url"]) + ">"
        for photo in post["photos"]:
            altSizes = photo["alt_sizes"]
            altSize = None
            for size in altSizes:
                if size["width"] > 420 and size["width"] <= 500:
                    altSize = size
            altSize = altSize if altSize is not None else altSizes[0]
            re += "<img src=%s width=\"%s\" height=\"%s\" />" % (quoteattr(altSize["url"]), altSize["width"], altSize["height"])
        if isLink:
            re += "</a>"
        re += post["caption"]
        if "source_url" in post:
            re += "<p><a href=%s>%s</a></p>" % (quoteattr(post["source_url"]), escape(post["source_title"]))
        return re
    elif type == "quote":
        re = "<blockquote>%s</blockquote>%s" % (post["text"], post["source"])
        if "source_url" in post:
            re += "<p><a href=%s>%s</a></p>" % (quoteattr(post["source_url"]), escape(post["source_title"]))
        return re
    elif type == "link":
        re = "<p><a href=%s>Link</a></p>%s" % (quoteattr(post["url"]), post["description"])
        if "source_url" in post:
            re += "<p><a href=%s>%s</a></p>" % (quoteattr(post["source_url"]), escape(post["source_title"]))
        return re
    elif type == "chat":
        #re = "<p>" + webhelpers.html.converters.nl2br(escape(post["body"])) + "</p>"
        re = "<p>" + escape(post["body"]).replace("\n", "\n<br />") + "</p>"
        if "source_url" in post:
            re += "<p><a href=%s>%s</a></p>" % (quoteattr(post["source_url"]), escape(post["source_title"]))
        return re
    elif type == "audio":
        re = "<p><audio src=%s controls=\"controls\">%s</audio></p>%s" % (quoteattr(post["audio_url"]), post["player"], post["caption"])
        if "source_url" in post:
            re += "<p><a href=%s>%s</a></p>" % (quoteattr(post["source_url"]), escape(post["source_title"]))
        return re
    elif type == "video":
        re = ""
        if "video_url" in post:
            videoUrl = quoteattr(post["video_url"])
            re += "<video src=%s controls=\"controls\" width=\"500\"><a href=%s>Video</a></video>" % (videoUrl, videoUrl)
        else:
            players = post["player"]
            re += players[len(players) - 1]["embed_code"]
        re += post["caption"]
        if "source_url" in post:
            re += "<p><a href=%s>%s</a></p>" % (quoteattr(post["source_url"]), escape(post["source_title"]))
        return re
    elif type == "answer":
        return "<dl><dt>%s</dt><dd>%s</dd></dl>" % (post["question"], post["answer"])

query = dict(urlparse.parse_qsl(os.environ.get("QUERY_STRING", "")))

if "id" not in query:
    print("Status: 400 Bad Request")
    print("Content-Type: text/plain; charset=utf-8")
    print
    print(u" ID が指定されていません。")
    sys.exit();

id = query["id"]
type = query.get("type", "")

db = MySQLdb.connect(user = dbName, passwd = dbPassword, db = dbName, charset = "utf8")
c = db.cursor()

c.execute("SELECT username, token, secret FROM %s WHERE id = %s"
    % (usersTable, db.literal(id))
)

sqlResult = c.fetchone()

if sqlResult is None:
    print("Status: 400 Bad Request")
    print("Content-Type: text/plain; charset=utf-8")
    print
    print(u"指定された ID が存在しません。")
    sys.exit();

c.execute("UPDATE %s SET lastaccess = NOW() WHERE id = %s"
    % (usersTable, db.literal(id))
)

db.commit()
c.close()
db.close()

reqUri = "http://api.tumblr.com/v2/user/dashboard"
if len(type) != 0:
    reqUri += "?type=" + type

client = oauth2.Client(oauthConsumer, oauth2.Token(sqlResult[1], sqlResult[2]))
resp, content = client.request(reqUri, "GET")

posts = json.loads(content)["response"]["posts"]

resRss = """<?xml version=\"1.0\" encoding=\"utf-8\"?>
<rss version=\"2.0\">
<channel>
<title>%s's Dashboard</title>
<link>http://www.tumblr.com/dashboard</link>
<description>%s</description>
<generator>TbrFeed</generator>
""" % (escape(sqlResult[0]), escape(type if len(type) != 0 else "all"))

for post in posts:
    resRss += """<item>
  <title>%s</title>
  <link>%s</link>
  <description>%s</description>
  <category>%s</category>
  <author>%s</author>
  <pubDate>%s</pubDate>
</item>\n""" % (escape(createTitle(post)),
        escape(post["post_url"]), escape(createDescription(post)),
        escape(post["type"]), escape(post["blog_name"]),
        escape(parse(post["date"]).strftime("%a, %d %b %Y %H:%M:%S GMT")))

resRss += "</channel>\n</rss>"

print("Content-Type: application/rss+xml; charset=utf-8")
print
print(resRss)
