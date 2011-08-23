import urllib
import urlparse
import logging
import pdb

from tornado import httpclient
from tornado import escape
from tornado.auth import OAuthMixin


class WeiboMixin(OAuthMixin):
    
    _OAUTH_REQUEST_TOKEN_URL = "http://api.t.sina.com.cn/oauth/request_token"
    _OAUTH_ACCESS_TOKEN_URL = "http://api.t.sina.com.cn/oauth/access_token"
    _OAUTH_AUTHORIZE_URL = "http://api.t.sina.com.cn/oauth/authorize"
    _OAUTH_NO_CALLBACKS = False

    def weibo_request(self, path, callback, access_token=None, 
                        post_args=None, **args):
        url = "http://api.t.sina.com.cn" + path + ".json"
        if access_token:
            all_args = {}
            all_args.update(args)
            all_args.update(post_args or {})
            consumer_token = self._oauth_consumer_token()
            method = "POST" if post_args is not None else "GET"
            oauth = self._oauth_request_parameters(
                    url, access_token, all_args, method=method)
            args.update(oauth)
        if args: url+= "?" + urllib.urlencode(args)
        callback = self.async_callback(self._on_weibo_request, callback)
        http = httpclient.AsyncHTTPClient()
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib.urlencode(post_args),
                       callback=callback)
        else:
            http.fetch(url, callback=callback)

    def _on_weibo_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error, 
                            response.request.url)
            callback(None)
            return
        callback(escape.json_decode(response.body))

    def _oauth_consumer_token(self):
        self.require_setting("weibo_consumer_key", "Weibo OAuth")
        self.require_setting("weibo_consumer_secret", "Weibo OAuth")
        
        return dict(key=self.settings["weibo_consumer_key"],
                    secret=self.settings["weibo_consumer_secret"])

    def _oauth_get_user(self, access_token, callback):
        callback = self.async_callback(self._parse_user_response, callback)
        '''pdb.set_trace()
        '''
        self.weibo_request(
                "/users/show/" + access_token["user_id"],
                access_token=access_token, callback=callback)

    def _parse_user_response(self, callback, user):
        if user:
            user["username"] = user["screen_name"]
        callback(user)
