import datetime
import re
import xml.sax.saxutils

import flask

import tumblr

def img_tag_from_photo(photo):
    alt_sizes = photo["alt_sizes"]
    alt_size = None
    for size in alt_sizes:
        if size["width"] > 420 and size["width"] <= 500:
            alt_size = size
    if not alt_size:
        alt_size = alt_sizes[0]
    return """<img src=%s width="%s" height="%s" />""" \
        % (xml.sax.saxutils.quoteattr(alt_size["url"]), alt_size["width"], alt_size["height"])

def create_title(post):
    title = post.get("title")
    if title:
        return post["title"]

    title = post["type"].capitalize()

    content = post.get("body")
    if not content: content = post.get("caption")
    if not content: content = post.get("text")
    if not content: content = post.get("description")
    if not content: content = post.get("question")

    if content:
        title += ": " + xml.sax.saxutils.unescape(re.sub(r"(\<.*?\>|[\r\n])", "", content))

    if len(title) > 60:
        title = title[:60-3] + "..."

    return title

def create_description(post):
    return flask.render_template("feed_%s.html" % (post["type"],), post=post, img_tag_from_photo=img_tag_from_photo)

def format_date(date_str):
    return tumblr.parse_date(date_str).strftime("%a, %d %b %Y %H:%M:%S GMT")

def generate_rss(uri, username, type, posts):
    return flask.render_template("rss.xml",
        uri=uri,
        username=username,
        type=type,
        posts=posts,
        create_title=create_title,
        create_description=create_description,
        parse_date=tumblr.parse_date)

def generate_atom(uri, username, type, posts):
    return flask.render_template("atom.xml",
        uri=uri,
        username=username,
        type=type,
        posts=posts,
        create_title=create_title,
        create_description=create_description,
        parse_date=tumblr.parse_date)
