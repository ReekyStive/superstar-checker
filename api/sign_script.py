import time
from aiohttp import ClientSession, ClientResponse


class Sign(object):
    """
    各类签到函数
    """

    def __init__(self, session: ClientSession, classid: str, courseid: str, activeid: str, sign_type: str):
        self.classid = classid
        self.courseid = courseid
        self.activeid = activeid
        self.sign_type = sign_type
        self.session = session
        # self.headers = {
        #     'Accept-Encoding': 'gzip, deflate',
        #     'Accept-Language': 'zh-CN,zh;q=0.9',
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'}

    async def general_sign(self):
        """普通签到"""
        url = 'https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign?activeId={}&classId={}&fid=&courseId={}'.format(
            self.activeid,
            self.classid,
            self.courseid)
        resp: ClientResponse
        async with self.session.get(url):
            return {
                'date': time.strftime("%m-%d %H:%M", time.localtime()),
                'status': 3000
            }

    async def hand_sign(self):
        """手势签到"""
        hand_sign_url = "https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/signIn?&courseId={}&classId={}&activeId={}".format(
            self.courseid, self.classid, self.activeid)
        async with self.session.get(hand_sign_url):
            return {
                'date': time.strftime("%m-%d %H:%M", time.localtime()),
                'status': 3001
            }

    async def qcode_sign(self, *, enc: str):
        """
        二维码签到
        @params enc: 校验码
        """
        if not enc:
            return {
                'date': time.strftime("%m-%d %H:%M", time.localtime()),
                'status': 4001
            }

        params = {
            'enc': enc,
            'name': '',
            'activeId': self.activeid,
            'uid': '',
            'clientip': '',
            'useragent': '',
            'latitude': '-1',
            'longitude': '-1',
            'fid': '',
            'appType': '15'
        }

        async with self.session.get('https://mobilelearn.chaoxing.com/pptSign/stuSignajax', params=params, allow_redirects=False) as resp:
            text = await resp.read()
            if "失败" in text.decode():
                return {
                    'date': time.strftime("%m-%d %H:%M", time.localtime()),
                    'status': 4002
                }

            return {
                'date': time.strftime("%m-%d %H:%M", time.localtime()),
                'status': 3004
            }

    async def addr_sign(self):
        """位置签到"""
        params = {
            'name': '',
            'activeId': self.activeid,
            'address': '中国',
            'uid': '',
            'clientip': '0.0.0.0',
            'latitude': '-2',
            'longitude': '-1',
            'fid': '',
            'appType': '15',
            'ifTiJiao': '1'
        }
        async with self.session.get(
                'https://mobilelearn.chaoxing.com/pptSign/stuSignajax',
                params=params):
            return {
                'date': time.strftime("%m-%d %H:%M", time.localtime()),
                'status': 3003
            }

    async def tphoto_sign(self):
        """拍照签到"""
        params = {
            'name': '',
            'activeId': self.activeid,
            'address': '中国',
            'uid': '',
            'clientip': '0.0.0.0',
            'latitude': '-2',
            'longitude': '-1',
            'fid': '',
            'appType': '15',
            'ifTiJiao': '1',
            'objectId': 'da82dee9f197a1ab22614efd39e20c14'
        }
        async with self.session.get(
                'https://mobilelearn.chaoxing.com/pptSign/stuSignajax',
                params=params):
            return {
                'date': time.strftime("%m-%d %H:%M", time.localtime()),
                'status': 3002
            }

    # def __get_token(self):
    #     """获取上传文件所需参数token"""
    #     url = 'https://pan-yz.chaoxing.com/api/token/uservalid'
    #     res = self.session.get(url, headers=self.headers)
    #     token_dict = json.loads(res.text)
    #     return (token_dict['_token'])
    #
    # def __upload_img(self):
    #     """上传图片"""
    #     # 从图片文件夹内随机选择一张图片
    #     all_img = os.listdir(IMAGE_PATH)
    #     img = IMAGE_PATH + random.choice(all_img)
    #     if len(all_img) == 0:
    #         return "da82dee9f197a1ab22614efd39e20c14"
    #     else:
    #         uid = self.session.cookies.get_dict()['UID']
    #         url = 'https://pan-yz.chaoxing.com/upload'
    #         files = {'file': (img, open(img, 'rb'),
    #                           'image/webp,image/*',), }
    #         res = self.session.post(url, data={'puid': uid, '_token': self.__get_token(
    #         )}, files=files, headers=self.headers)
    #         res_dict = json.loads(res.text)
    #         return (res_dict['objectId'])
