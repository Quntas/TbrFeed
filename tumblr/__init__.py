import datetime
import json
import re
import urllib.parse
import urllib.request

from tumblr import oauth

class Tumblr:
    def __init__(self, consumer_key, consumer_secret, oauth_token=None, oauth_token_secret=None):
        self._api_endpoint = "http://api.tumblr.com/v2/"
        self._oauth_endpoint = "http://www.tumblr.com/oauth/"
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

    def _http_request(self, uri, params=None, method=None, callback=None, verifier=None):
        if not method:
            method = "POST" if params else "GET"
        auth_header = oauth.create_authorization_header(
            method,
            uri,
            None,
            self.consumer_key,
            self.consumer_secret,
            self.oauth_token,
            self.oauth_token_secret,
            oauth.HMACSHA1,
            callback,
            verifier,
            params
        )
        data = oauth.to_wwwformurlencoded(params).encode("utf-8") if params else None
        request = urllib.request.Request(uri, data, {"Authorization": auth_header}, method=method)
        return urllib.request.urlopen(request)

    def request_token(self, callback=None):
        response = self._http_request(self._oauth_endpoint + "request_token", None, "POST", callback)
        dic = urllib.parse.parse_qs(response.read().decode("utf-8"))
        self.oauth_token = dic["oauth_token"][0]
        self.oauth_token_secret = dic["oauth_token_secret"][0]

    def get_authorize_uri(self):
        return self._oauth_endpoint + "authorize?oauth_token=" + self.oauth_token

    def access_token(self, verifier):
        response = self._http_request(self._oauth_endpoint + "access_token", method="POST", verifier=verifier)
        dic = urllib.parse.parse_qs(response.read().decode("utf-8"))
        self.oauth_token = dic["oauth_token"][0]
        self.oauth_token_secret = dic["oauth_token_secret"][0]

    def user_info(self):
        response = self._http_request(self._api_endpoint + "user/info")
        return json.loads(response.read().decode("utf-8"))["response"]["user"]

    def user_dashboard(self, type=None):
        uri = self._api_endpoint + "user/dashboard"
        if type: uri += "?type=" + urllib.parse.quote(type)
        response = self._http_request(uri)
        return json.loads(response.read().decode("utf-8"))["response"]["posts"]

def parse_date(date_str):
    match = re.match(r"^(\d{4})\-(\d{2})\-(\d{2}) (\d{2}):(\d{2}):(\d{2}) GMT$", date_str)
    return datetime.datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5)), int(match.group(6)))