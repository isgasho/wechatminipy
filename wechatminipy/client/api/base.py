class BaseWechatMiniAppApi:
    BASE_API_URL = ""

    def __init__(self, client=None):
        self._client = client

    @property
    def access_token(self):
        return self._client.access_token

    def register_client(self, client):
        if not self._client:
            self._client = client

