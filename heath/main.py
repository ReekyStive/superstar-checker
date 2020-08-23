import json
from urllib import parse
from urllib.parse import quote
import requests

# 学习通账号密码
USER_INFO = {
    'username': '###',
    'password': '###',
    'schoolid': '',  # 学号登录才需要填写
}


class HeathReport(object):

    def __init__(self, username: str, password: str, schoolid: str = ""):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self._username = USER_INFO['username']
        self._password = USER_INFO['password']
        self._schoolid = USER_INFO['schoolid']
        self._session = requests.session()
        self._session.headers = headers
        self.form_data = []

    def _login(self):
        """
        登录: 支持手机和邮箱登录
        """
        params = {
            "name": self._username,
            "pwd": self._password,
            "verify": "0",
            "schoolid": self._schoolid if self._schoolid else ""
        }
        api = "https://passport2.chaoxing.com/api/login"
        r = self._session.get(api, params=params)
        if r.status_code == 403:
            return 1002
        data = json.loads(r.text)
        if data['result']:
            print("登录成功")
            return 1000  # 登录成功
        else:
            return 1001  # 登录信息有误

    def _get_last_heath_info(self):
        """
        获取上次提交的健康信息

        """
        params = {
            "cpage": "1",
            "formId": "7185",
            "enc": "f837c93e0de9d9ad82db707b2c27241e",
            "formAppId": ""
        }
        api = 'http://office.chaoxing.com/data/web/apps/forms/fore/user/list'
        resp = self._session.get(api, params=params)
        raw_data = json.loads(resp.text)
        return raw_data

    @staticmethod
    def clean_heath_info(raw_data: dict) -> list:
        form_data = raw_data['data']['formUserList'][0]['formData']
        d = {
            "inDetailGroupIndex": -1,
            "fromDetail": False,
        }
        not_show = [x for x in range(9, 36) if x % 2 != 0]
        not_show.extend([38, 39, 41, 42])
        for f in form_data:
            f.update(d)

            if f['id'] == 5:
                f['fields'][0]['tip']['text'] = r"<p+style=\"text-align:+center;\"><span+style=\"font-size:+large;+font-weight:+bold;\">基本信息</span></p>"
            elif f['id'] == 6:
                f['fields'][0]['tip']['text'] = r"<p+style=\"text-align:+center;\"><span+style=\"font-size:+large;+font-weight:+bold;\">健康状况</span></p>"
            elif f['id'] == 36:
                f['fields'][0]['tip']['text'] = r"<p+style=\"text-align:+center;\"><span+style=\"font-size:+large;+font-weight:+bold;\">出行情况</span></p>"
            elif f['id'] == 8:
                f['fields'][0]['values'][0]['val'] = "健康+"
                f['fields'][0]['options'][0]['title'] = "健康+"

            if f['id'] in not_show:
                f['isShow'] = False
            else:
                f['isShow'] = True
        # print(form_data)
        return form_data

    def _edit_report(self, hid: str, enc: str):
        """
        上报健康信息
        """
        data = {
            "id": hid,
            "formId": "7185",
            "enc": enc,
            "gverify": "",
            "formData": ''
        }
        payload = parse.urlencode(data)
        str_form_data = str(self.form_data)
        str_form_data = str_form_data.replace('\'', '\"').replace('False', 'false').replace('True', 'true').replace(r"\\", "\\")
        payload += quote(str_form_data, 'utf-8')
        # 修改表单信息的API
        edit_api = "https://office.chaoxing.com/data/apps/forms/fore/user/edit"
        resp = self._session.post(edit_api, data=payload)
        print(resp.text)

    def _to_begin(self):
        """
        调用登录及健康信息获取函数
        """
        self._login()
        raw_data = self._get_last_heath_info()
        self.form_data = self.clean_heath_info(raw_data)

    def edit_report(self, hid: str, enc: str):
        """
        修改已上报的健康信息
        说明：修改已上报信息的功能实际意义不大，主要是开发时测试使用
        :params id: 表单id
        :params form_data: 已编码的上次健康信息
        """
        self._to_begin()
        self._edit_report(hid, enc)

    def daily_report(self):
        """
        每日健康信息上报
        今天没打卡机会了，明天测试
        估计与修改上报信息相差不大
        """
        pass


if __name__ == '__main__':
    h = HeathReport(username=USER_INFO['username'], password=USER_INFO['password'])
    h.edit_report(hid="#########", enc="########")

