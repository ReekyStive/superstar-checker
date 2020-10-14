# -*- coding: utf8 -*-
import re
import json
import asyncio
import traceback
import logging
from typing import Optional, List, Dict
from aiohttp import ClientSession
from lxml import etree
from bs4 import BeautifulSoup
from config import STATUS_CODE_DICT
from db_handler import SignMongoDB
from sign_script import Sign

HEADERS = {
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'
}


class AutoSign(object):

    def __init__(self, session: ClientSession, username: str, password: str, schoolid: str = None):
        """初始化就进行登录
        @param session:
        @param username: 用户[学号]
        @param password: 密码
        @param schoolid: 学校ID[仅学号登录填写]
        """
        self.session = session
        self.username = username
        self.password = password
        self.schoolid = schoolid
        self.mongo = SignMongoDB(username)

    async def is_new_user(self) -> None:
        """
        判断是否为新用户
        @return:
        """
        if not await self.mongo.find_old_user():
            await self.mongo.create_new_user()

    async def set_cookies(self) -> int:
        """设置cookies
        @return:
        """
        code: int = 1000  # 登录信息有误
        if not await self.check_cookies():
            # 无效则重新登录，并保存cookies
            login_status: dict = await self.login()
            # 1000 有效， 1001 无效
            code = login_status['code']
            if code == 1000:
                await self.save_cookies(login_status['cookies'])
        return code

    async def save_cookies(self, cookies: dict):
        """保存cookies"""
        await self.mongo.save_cookie(cookies)

    async def check_cookies(self) -> bool:
        """
        验证cookies
        @return:
        """
        # 从数据库内取出cookie
        status: bool = False
        cookies = await self.mongo.get_cookie()

        if not cookies:
            return status

        self.session.cookie_jar.update_cookies(cookies)

        # 验证cookies
        async with self.session.get('http://mooc1-1.chaoxing.com', allow_redirects=False) as resp:
            if resp.status != 200:
                print("cookies已失效")
                status = False
            else:
                print("cookies有效")
                status = True
        return status

    async def login(self) -> dict:
        # 登录-手机邮箱登录
        url = 'https://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid={}&verify=0'.format(self.username,
                                                                                                    self.password,
                                                                                                    self.schoolid if self.schoolid else "")
        code: int
        cookies: dict = {}
        async with self.session.get(url) as resp:
            if resp.status == 403:
                code = 1002
                return {
                    'code': code,
                    'cookies': cookies
                }
            data = json.loads(await resp.read())
            if data['result']:
                # return 1000  # 登录成功
                code = 1000
                cookies = resp.cookies
            else:
                # 登录信息有误
                code = 1001
            return {
                'code': code,
                'cookies': cookies
            }

    async def check_activeid(self, activeid: str) -> bool:
        """
        用于判断当前签到是否已被执行
        @param activeid: 活动id，用于判断当前签到是否已被执行
        @return:
        """
        activeid_lists: list = await self.mongo.get_text_activeid()
        if activeid in activeid_lists:
            return True
        else:
            return False

    @staticmethod
    def class_info(res: List[Dict], soup: BeautifulSoup) -> List[Dict]:
        """
        整理课程信息courseid， classid， classname
        @param res:
        @param soup:
        @return:
        """
        course_id_list = soup.find_all('input', attrs={'name': 'courseId'})
        class_id_list = soup.find_all('input', attrs={'name': 'classId'})
        classname_list = soup.find_all('h3', class_="clearfix")

        # 用户首次使用，将所用有的classid保存
        for i, v in enumerate(course_id_list):
            res.append({
                'classid': class_id_list[i]['value'],
                'courseid': v['value'],
                'classname': classname_list[i].find_next('a').text
            })
            # res.append((v['value'], class_id_list[i]['value'],
            #             classname_list[i].find_next('a').text))
        return res

    async def get_all_classid(self) -> List[Dict]:
        """
        获取课程主页中所有课程的classid和courseid
        """
        res: List[Dict] = await self.mongo.get_all_classid_and_courseid()
        # 之前的存储为List[List]
        if res and isinstance(res[0], list):
            # 将之前的存储格式更新为List[Dict]
            await self.update_courseid()
            res: List[Dict] = await self.mongo.get_all_classid_and_courseid()

        # 数据库查找，没有则新获取
        if not res:
            async with self.session.get('http://mooc1-2.chaoxing.com/visit/interaction') as resp:
                soup = BeautifulSoup(await resp.read(), "lxml")

            res = self.class_info(res, soup)
            await self.mongo.save_all_classid_and_courseid(res)
        return res

    async def update_courseid(self) -> dict:
        """
        更新用户课程ID
        @return:
        """
        res: List[Dict] = []
        async with self.session.get('http://mooc1-2.chaoxing.com/visit/interaction') as resp:
            soup = BeautifulSoup(await resp.read(), "lxml")

        res = self.class_info(res, soup)
        await self.mongo.update_courseid(res)
        return {
            'code': 3006,
            'message': STATUS_CODE_DICT[3006]
        }

    async def get_sign_type(self, classid: str, courseid: str, activeid: str) -> str:
        """
        获取签到类型
        """
        sign_url = 'https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign?activeId={}&classId={}&courseId={}'.format(
            activeid, classid, courseid)
        async with self.session.get(sign_url) as resp:
            h = etree.HTML(await resp.read())
        sign_type: list = h.xpath('//div[@class="location"]/span/text()')
        return sign_type[0]

    async def get_activeid(self, classid: str, courseid: str, classname: str) -> Optional[Dict]:
        """
        访问任务面板获取课程的活动id
        """

        res: list = []
        re_rule = r'([\d]+),2'
        url: str = 'https://mobilelearn.chaoxing.com/widget/pcpick/stu/index?courseId={}&jclassId={}'.format(
            courseid, classid)
        async with self.session.get(url) as resp:
            h = etree.HTML(await resp.read())

        activeid_list = h.xpath('//*[@id="startList"]/div/div/@onclick')

        for activeid in activeid_list:
            activeid = re.findall(re_rule, activeid)
            if not activeid:
                continue
            sign_type: str = await self.get_sign_type(classid, courseid, activeid[0])
            res.append((activeid[0], sign_type))

        count = len(res)
        if count != 0:
            # d['count'] 此次签到有几门课程
            # d['class'] 此次签到所有课程的信息
            d = {'count': count, 'class': {}}
            for i in range(count):
                if await self.check_activeid(res[i][0]):
                    continue
                d['class'][i] = {
                    'classid': classid,
                    'courseid': courseid,
                    'activeid': res[i][0],
                    'classname': classname,
                    'sign_type': res[i][1]
                }
            return d

    async def sign_in_type_judgment(self, classid: str, courseid: str, activeid: str, sign_type: str) -> dict:
        """
        判断签到类型
        """
        res: dict
        sign = Sign(self.session, classid, courseid, activeid, sign_type)

        if "手势" in sign_type:
            res = await sign.hand_sign()

        elif "二维码" in sign_type:
            res = await sign.qcode_sign()

        elif "位置" in sign_type:
            res = await sign.addr_sign()

        elif "拍照" in sign_type:
            res = await sign.tphoto_sign()

        else:
            res = await sign.general_sign()

        return res

    async def sign_tasks_run(self) -> dict:
        """开始所有签到任务"""
        tasks: list = []
        message: str = ''
        signed_list: List[Dict] = []

        # 获取所有课程的classid和course_id
        class_infos: List[Dict] = await self.get_all_classid()

        # 使用协程获取所有课程activeid和签到类型
        for info in class_infos:
            coroutine = self.get_activeid(classid=info['classid'],
                                          courseid=info['courseid'],
                                          classname=info['classname'])
            tasks.append(coroutine)

        result: List[Optional[Dict]] = await asyncio.gather(*tasks)
        # print('执行结果->', result)
        for r in result:
            if not r:
                continue
            for d in r['class'].values():
                sign_res: dict = await self.sign_in_type_judgment(
                    d['classid'],
                    d['courseid'],
                    d['activeid'],
                    d['sign_type'])

                # 签到课程， 签到时间， 签到状态
                sign_msg = {
                    'name': d['classname'],
                    'date': sign_res['date'],
                    'status': STATUS_CODE_DICT[sign_res['status']]
                }
                # 将签到成功activeid保存至数据库
                await self.mongo.save_text_activeid(d['activeid'])
                signed_list.append(sign_msg)
        if signed_list:
            code = 2001
            # message: str = ''
        else:
            code = 2000
            message = STATUS_CODE_DICT[2000]
        return {
            'code': code,
            'signed_list': signed_list,
            'message': message
        }


# def server_chan_send(msgs, sckey=None):
#     """server酱将消息推送至微信"""
#     desp = ''
#     for msg in msgs:
#         desp = '|  **课程名**  |   {}   |\r\r| :----------: | :---------- |\r\r'.format(
#             msg['name'])
#         desp += '| **签到时间** |   {}   |\r\r'.format(msg['date'])
#         desp += '| **签到状态** |   {}   |\r\r'.format(msg['status'])
#
#     params = {
#         'text': '您的网课签到消息来啦！',
#         'desp': desp
#     }
#     # if sckey:
#     #     requests.get('https://sc.ftqq.com/{}.send'.format(sckey), params=params)
# async def update_courseid(username: str, password)

async def run(
        session: ClientSession,
        username: str,
        password: str,
        schoolId: Optional[str] = None,
        sckey: Optional[str] = None,
        task_type: Optional[str] = 'sign'
) -> dict:
    """
    脚本入口
    @param session:
    @param username:
    @param password:
    @param schoolId:
    @param sckey:
    @param task_type: 任务类型： sign签到; update更新
    @return:
    """
    result: dict = {}
    try:
        auto_sign = AutoSign(session, username, password, schoolId)
        await auto_sign.is_new_user()
        login_status = await auto_sign.set_cookies()

        if login_status != 1000:
            return {
                'msg': login_status,
                'message': '登录失败，' + STATUS_CODE_DICT[login_status]
            }
        if task_type == 'sign':
            result = await auto_sign.sign_tasks_run()
        elif task_type == 'update':
            result = await auto_sign.update_courseid()
        elif task_type == 'bind':
            result = {}
        # message = result['message']
        # if result['msg'] == 2001:
        #     server_chan_send(detail, sckey)
        # print('执行完毕')
        # return result

    except Exception:
        logging.basicConfig(filename='logs.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.error(traceback.format_exc())
        result = {'msg': 4000, 'message': STATUS_CODE_DICT[4000]}
    print(result)
    return result
