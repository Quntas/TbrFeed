import base64
import hashlib
import hmac
import random
import time
import urllib.parse

HMACSHA1 = "HMAC-SHA1"
RSASHA1 = "RSA-SHA1"
PLAINTEXT = "PLAINTEXT"

OAUTH_VERSION = "1.0"

ALLOWED_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-._~"

def percent_encode(text):
    return "".join(c if ALLOWED_CHARS.find(c) != -1 else "".join("%%%X" % b for b in c.encode("utf-8")) for c in text)

def normalize_uri(uri):
    parsed_uri = urllib.parse.urlparse(uri)
    return "%s://%s%s%s" % (parsed_uri.scheme, parsed_uri.hostname, "" if parsed_uri.port is None or (parsed_uri.scheme == "http" and parsed_uri.port == 80) or (parsed_uri.scheme == "https" and parsed_uri.port == 443) else ":" + str(parsed_uri.port), parsed_uri.path)

def normalize_parameters(params):
    return "&".join(percent_encode(item[0]) + "=" + percent_encode(item[1]) for item in sorted(dict(params).items(), key = lambda item: item[0]))

def parse_wwwformurlencoded(source):
    return dict((urllib.parse.unquote(s[0]), urllib.parse.unquote(s[1]) if len(s) > 1 else "") for s in (_.split("=") for _ in source.lstrip("?").split("&") if _))

def to_wwwformurlencoded(source):
    return "&".join(urllib.parse.quote(item[0]) + "=" + urllib.parse.quote(item[1]) for item in dict(source).items())

def timestamp():
    return str(int(time.time()))

def nonce():
    return "".join(random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz") for i in range(42))

def sign_parameters_base(realm, consumer_key, token, signature_method, timestamp, nonce, callback, verifier):
    dic = {"oauth_version": OAUTH_VERSION}

    if realm: dic["realm"] = realm
    if consumer_key: dic["oauth_consumer_key"] = consumer_key
    if token: dic["oauth_token"] = token
    if signature_method: dic["oauth_signature_method"] = signature_method
    if timestamp: dic["oauth_timestamp"] = timestamp
    if nonce: dic["oauth_nonce"] = nonce
    if callback: dic["oauth_callback"] = callback
    if verifier: dic["oauth_verifier"] = verifier

    return dic

def signature_base(http_method, uri, sign_params, params):
    base_params = dict(sign_params)
    if params: base_params.update(params)
    base_params.update(parse_wwwformurlencoded(urllib.parse.urlparse(uri).query))

    return "&".join((
        http_method.upper(),
        percent_encode(normalize_uri(uri)),
        percent_encode(normalize_parameters(base_params))
    ))

def signature_key(consumer_secret, token_secret):
    return percent_encode(consumer_secret if consumer_secret else "") + "&" + percent_encode(token_secret if token_secret else "")

def signature(basestring, key, signature_method):
    if signature_method == HMACSHA1:
        return base64.b64encode(hmac.new(key.encode("ascii"), basestring.encode("ascii"), hashlib.sha1).digest()).decode("ascii")
    elif signature_method == PLAINTEXT:
        return key
    else:
        raise NotImplementedError()

def sign_parameters(http_method, uri, realm, consumer_key, consumer_secret, token, token_secret, signature_method, callback, verifier, params):
    is_plaintext = signature_method == PLAINTEXT
    sign_params = sign_parameters_base(realm, consumer_key, token, signature_method, None if is_plaintext else timestamp(), None if is_plaintext else nonce(), callback, verifier)
    sign_params["oauth_signature"] = signature(signature_base(http_method, uri, sign_params, params), signature_key(consumer_secret, token_secret), signature_method)
    return sign_params

def create_authorization_header(http_method, uri, realm, consumer_key, consumer_secret, token, token_secret, signature_method, callback, verifier, params):
    return "OAuth " + ",".join(
        percent_encode(item[0]) + "=" + percent_encode(item[1])
        for item in sign_parameters(http_method, uri, realm, consumer_key, consumer_secret, token, token_secret, signature_method, callback, verifier, params).items()
    )
