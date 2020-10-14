from typing import List, Dict
import motor.motor_asyncio
from motor.motor_asyncio import core


class SignMongoDB(object):

    def __init__(self, username: str):
        self.client: core.AgnosticClient = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
        database: core.AgnosticDatabase = self.client["signweb"]
        self.collection: core.AgnosticCollection = database["users"]
        self.username = username

    async def find_old_user(self):
        """
        @return:
        """
        return await self.collection.find_one({"username": self.username})

    async def create_new_user(self) -> None:
        """
        新建用户
        @return:
        """
        await self.collection.insert_one({"username": self.username})

    async def get_cookie(self) -> dict:
        """从数据库内取出cookie"""
        try:
            x = await self.collection.find_one({"username": self.username}, {"cookie": 1.0})
            return x['cookie']
        except KeyError:
            pass
        except TypeError:
            pass
        return {}

    async def save_cookie(self, cookie: dict) -> None:
        """保存cookie到数据库"""
        # 如果cookie失效，先从数据库删除旧的cookie
        # 再保存新的cookie
        await self.collection.update_one({"username": self.username}, {"$unset": {"cookie": ""}})
        await self.collection.update_one({"username": self.username}, {"$set": {"cookie": cookie}})

    async def get_all_classid_and_courseid(self) -> List[Dict]:
        """获取此用户所有的课程id"""
        cursor = await self.collection.find_one({"username": self.username}, {"cclist": 1.0})
        result = []
        try:
            result = cursor['cclist']
        except KeyError:
            pass
        except TypeError:
            pass
        return result

    async def save_all_classid_and_courseid(self, cclists: List[Dict]):
        """
        保存此用户所有的课程id
        """
        for cclist in cclists:
            await self.collection.update_one({"username": self.username},
                                             {"$addToSet": {"cclist": cclist}})

    async def update_courseid(self, new_courseid: List[Dict]) -> None:
        """
        更新courseid
        """
        await self.collection.update_one({"username": self.username},
                                         {"$unset": {"cclist": ""}})
        await self.collection.update_one({"username": self.username},
                                         {"$set": {"cclist": new_courseid}})

    async def save_text_activeid(self, activeid: str) -> None:
        """
        记录已签到过的活动id
        @param activeid:
        @return:
        """
        await self.collection.update_one({"username": self.username},
                                         {"$addToSet": {"activeid": activeid}})

    async def get_text_activeid(self) -> list:
        """
        获取前10个已签到activeid
        """
        sort = [(u"_id", -1)]
        res = await self.collection.find_one({"username": self.username}, {"activeid": 1.0}, sort=sort, limit=10)
        try:
            return res["activeid"]
        except:
            return []

    async def set_test_data(self):
        await self.collection.insert_one(
            {"username": self.username, "cookie": 11111, "activeid": [1, 2], "classid": [8, 9], "courseid": [8, 9]})

