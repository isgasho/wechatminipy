from wechatminipy.client.api.base import BaseWechatMiniAppApi


class WechatMiniAppTemplate(BaseWechatMiniAppApi):

    BASE_API_URL = "https://api.weixin.qq.com/cgi-bin/message/wxopen/template"

    def get_template_library_list(self):
        raise NotImplementedError()

    def delete_template(self):
        raise NotImplementedError()

    def get_template_library_by_id(self):
        raise NotImplementedError()

    def add_template(self):
        raise NotImplementedError()

    def get_template_list(self):
        raise NotImplementedError()

    def send_template_message(
        self, open_id, template_id, form_id, data, page=None, emphasis_keyword=None
    ):
        """
        发送小程序模板消息 Doc:
        https://developers.weixin.qq.com/miniprogram/dev/api/sendTemplateMessage.html
        """
        url = f"{self.BASE_API_URL}/send?access_token={self.access_token}"
        post_data = {
            "touser": open_id,
            "template_id": template_id,
            "form_id": form_id,
            "data": data,
            "page": page,
            "emphasis_keyword": emphasis_keyword,
        }
        return self._client.post(url, data=post_data)
