import json
import time

import requests

from wechatminipy.client.api.template import WechatMiniAppTemplate
from wechatminipy.client.exception import WeChatClientException


class WechatMiniAppClient:
    _session = requests.Session()

    template = WechatMiniAppTemplate()

    def __new__(cls, *arg, **kw):
        self = super().__new__(cls)
        self.template.register_client(self)
        return self

    def __init__(self, redis, app_id=None, app_secret=None, ns="WECHAT_"):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redis = redis
        self.ns = ns

        self.session = self._session
        self._expires_at = None

    def init_app(self, app):
        """for flask app"""
        opts = app.config.get_namespace(self.ns).copy()
        self.app_id = opts.get("app_id")
        self.app_secret = opts.get("app_secret")

    @property
    def key_of_access_token(self):
        return f"redis.key.access.token.{self.app_id}"

    @property
    def expires_at(self):
        if not self._expires_at:
            self._expires_at = (
                int(time.time()) + self.redis.ttl(self.key_of_access_token) - 10
            )
        return self._expires_at

    @expires_at.setter
    def expires_at(self, expires_at):
        self._expires_at = expires_at

    @property
    def access_token(self):
        if int(time.time()) > self.expires_at:
            return self.fetch_access_token()["access_token"]
        return self.redis.get(self.key_of_access_token).decode()

    def _handle_request_result(self, result):
        if not isinstance(result, dict):
            return result

        if "errcode" in result and result["errcode"] != 0:
            raise WeChatClientException(result["errcode"], result["errmsg"])
        return result

    def _fetch_access_token(self, url, params):
        """ The real fetch access token """
        res = self.session.get(url=url, params=params)
        result = res.json()
        result = self._handle_request_result(result)
        expires_in = 7200
        if "expires_in" in result:
            expires_in = result["expires_in"]
        self.redis.set(self.key_of_access_token, result["access_token"], ex=expires_in)
        self.expires_at = int(time.time()) + expires_in - 10
        return result

    def fetch_access_token(self):
        """
        获取 access token
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=通用接口文档

        :return: 返回的 JSON 数据包
        """
        return self._fetch_access_token(
            url="https://api.weixin.qq.com/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": self.app_id,
                "secret": self.app_secret,
            },
        )

    def post(self, url, **kw):
        if isinstance(kw.get("data", ""), dict):
            body = json.dumps(kw["data"], ensure_ascii=False)
            body = body.encode("utf-8")
            kw["data"] = body
        res = self.session.post(url, **kw)
        return self._handle_request_result(res.json())
