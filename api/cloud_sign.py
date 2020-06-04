# -*- coding: utf8 -*-
import re
import json
import asyncio
import logging
import requests
import traceback
from lxml import etree
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings()
from config import *
from db_handler import *
from sign_script import *


class AutoSign(object):

    def __init__(self, username, password, schoolid=None):
        """初始化就进行登录"""
        self.headers = {
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'}
        self.session = requests.session()
        self.session.headers = self.headers
        self.username = username
        self.password = password
        self.schoolid = schoolid
        self.mongo = SignMongoDB(username)

    def set_cookies(self):
        """设置cookies"""
        if not self.check_cookies():
            # 无效则重新登录，并保存cookies
            login_status = self.login()
            if login_status == 1000:
                self.save_cookies()
            else:
                return 1001
        return 1000

    def save_cookies(self):
        """保存cookies"""
        new_cookies = self.session.cookies.get_dict()
        self.mongo.to_save_cookie(new_cookies)

    def check_cookies(self):
        """验证cookies"""
        # 从数据库内取出cookie
        try:
            cookies = self.mongo.to_get_cookie()
        except:
            return False

        # session设置cookies
        cookies_jar = requests.utils.cookiejar_from_dict(cookies)

        self.session.cookies = cookies_jar
        # 验证cookies
        r = self.session.get(
            'http://mooc1-1.chaoxing.com/api/workTestPendingNew',
            allow_redirects=False)
        if r.status_code != 200:
            print("cookies已失效")
            return False
        else:
            print("cookies有效哦")
            return True

    def login(self):
        # 登录-手机邮箱登录
        r = self.session.get(
            'https://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid={}&verify=0'.format(
                self.username, self.password, self.schoolid if self.schoolid else ""), headers=self.headers)
        if r.status_code == 403:
            return 1002
        data = json.loads(r.text)
        if data['result']:
            print("登录成功")
            return 1000  # 登录成功
        else:
            return 1001  # 登录信息有误

    def check_activeid(self, activeid: str):
        """验证当前活动id是否已存在"""
        activeid_lists = self.mongo.to_get_istext_activeid()
        if activeid in activeid_lists:
            return True
        else:
            return False

    def get_all_classid(self) -> list:
        """获取课程主页中所有课程的classid和courseid"""
        res = []
        # 首先去数据库里寻找
        res = self.mongo.to_get_all_classid_and_courseid()
        if not res:
            r = self.session.get(
                'http://mooc1-2.chaoxing.com/visit/interaction',
                headers=self.headers)
            soup = BeautifulSoup(r.text, "lxml")
            courseId_list = soup.find_all('input', attrs={'name': 'courseId'})
            classId_list = soup.find_all('input', attrs={'name': 'classId'})
            classname_list = soup.find_all('h3', class_="clearfix")

            # 用户首次使用，可以将所用有的classid保存
            for i, v in enumerate(courseId_list):
                res.append((v['value'], classId_list[i]['value'],
                            classname_list[i].find_next('a').text))
            self.mongo.to_save_all_classid_and_courseid(res)
        return res

    def get_sign_type(self, classid, courseid, activeid):
        """获取签到类型"""
        sign_url = 'https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign?activeId={}&classId={}&courseId={}'.format(
            activeid, classid, courseid)
        response = self.session.get(sign_url, headers=self.headers)
        h = etree.HTML(response.text)
        sign_type = h.xpath('//div[@class="location"]/span/text()')
        return sign_type

    async def get_activeid(self, classid, courseid, classname):
        """访问任务面板获取课程的活动id"""
        re_rule = r'([\d]+),2'
        r = self.session.get(
            'https://mobilelearn.chaoxing.com/widget/pcpick/stu/index?courseId={}&jclassId={}'.format(
                courseid, classid), headers=self.headers, verify=False)
        res = []
        h = etree.HTML(r.text)
        activeid_list = h.xpath('//*[@id="startList"]/div/div/@onclick')
        for activeid in activeid_list:
            activeid = re.findall(re_rule, activeid)
            if not activeid:
                continue
            sign_type = self.get_sign_type(classid, courseid, activeid[0])
            res.append((activeid[0], sign_type[0]))

        n = len(res)
        if n != 0:
            d = {'num': n, 'class': {}}
            for i in range(n):
                if self.check_activeid(res[i][0]):
                    continue
                d['class'][i] = {
                    'classid': classid,
                    'courseid': courseid,
                    'activeid': res[i][0],
                    'classname': classname,
                    'sign_type': res[i][1]
                }
            return d

    def sign_in_type_judgment(self, classid, courseid, activeid, sign_type):
        """签到类型的逻辑判断"""
        s = Sign(self.session, classid, courseid, activeid, sign_type)
        if "手势" in sign_type:
            return s.hand_sign()
        elif "二维码" in sign_type:
            return s.qcode_sign()
        elif "位置" in sign_type:
            return s.addr_sign()
        elif "拍照" in sign_type:
            return s.tphoto_sign()
        else:
            return s.general_sign()

    def sign_tasks_run(self):
        """开始所有签到任务"""
        tasks = []
        res = []
        # 获取所有课程的classid和course_id
        classid_courseId = self.get_all_classid()

        # 使用协程获取所有课程activeid和签到类型
        for i in classid_courseId:
            coroutine = self.get_activeid(i[1], i[0], i[2])
            tasks.append(coroutine)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        print(result)
        for r in result:
            if r:
                for d in r['class'].values():
                    s = self.sign_in_type_judgment(
                        d['classid'],
                        d['courseid'],
                        d['activeid'],
                        d['sign_type'])

                    # 签到课程， 签到时间， 签到状态
                    sign_msg = {
                        'name': d['classname'],
                        'date': s['date'],
                        'status': STATUS_CODE_DICT[s['status']]
                    }
                    # 将签到成功activeid保存至数据库
                    self.mongo.to_save_istext_activeid(d['activeid'])
                    res.append(sign_msg)
        if res:
            final_msg = {
                'msg': 2001,
                'detail': res,
            }
        else:
            final_msg = {
                'msg': 2000,
                'detail': STATUS_CODE_DICT[2000]
            }
        return final_msg


def server_chan_send(msgs, sckey=None):
    """server酱将消息推送至微信"""
    desp = ''
    for msg in msgs:
        desp = '|  **课程名**  |   {}   |\r\r| :----------: | :---------- |\r\r'.format(
            msg['name'])
        desp += '| **签到时间** |   {}   |\r\r'.format(msg['date'])
        desp += '| **签到状态** |   {}   |\r\r'.format(msg['status'])

    params = {
        'text': '您的网课签到消息来啦！',
        'desp': desp
    }
    if sckey:
        requests.get('https://sc.ftqq.com/{}.send'.format(sckey), params=params)


def interface(user_info, sckey):
    try:
        s = AutoSign(user_info['username'], user_info['password'], user_info['schoolid'])
        login_status = s.set_cookies()
        print(login_status)
        if login_status != 1000:
            return {
                'msg': login_status,
                'detail': '登录失败，' + STATUS_CODE_DICT[login_status]
            }

        result = s.sign_tasks_run()
        detail = result['detail']
        if result['msg'] == 2001:
            server_chan_send(detail, sckey)
        print('执行完毕')
        return result

    except Exception as e:
        logging.basicConfig(filename='logs.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.error(traceback.format_exc())
        return {'msg': 4000, 'detail': STATUS_CODE_DICT[4000]}
