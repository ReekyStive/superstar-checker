import asyncio
import uvicorn
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from aiohttp import ClientSession, TCPConnector
import cloud_sign
from cloud_sign import HEADERS

app = FastAPI()


class User(BaseModel):
    username: str
    password: str
    schoolid: Optional[str] = None
    sckey: Optional[str] = None


@app.get('/sign')
@app.post('/sign')
async def sign(username: str,
               password: str,
               schoolid: Optional[str] = None,
               sckey: Optional[str] = None) -> dict:
    """
    签到
    @param username:
    @param password:
    @param schoolid:
    @param sckey:
    @return:
    """
    semaphore = asyncio.Semaphore(20)

    async with semaphore:
        async with ClientSession(headers=HEADERS, connector=TCPConnector(limit=2)) as session:
            return await cloud_sign.run(session=session,
                                        username=username,
                                        password=password,
                                        schoolId=schoolid,
                                        sckey=sckey)


@app.get('/updatecourseid')
@app.post('/updatecourseid')
async def update_courseid(username: str,
                          password: str,
                          schoolid: Optional[str] = None,
                          sckey: Optional[str] = None) -> dict:
    """
    更新课程ID
    @param username:
    @param password:
    @param schoolid:
    @param sckey:
    @return:
    """
    async with ClientSession(headers=HEADERS) as session:
        return await cloud_sign.run(session=session,
                                    username=username,
                                    password=password,
                                    schoolId=schoolid,
                                    sckey=sckey,
                                    task_type='update')


# @app.post('/sign')
# async def sign(user: User) -> dict:
#     """
#     签到
#     @param user:
#     @return:
#     """
#     return await cloud_sign.run(username=user.username,
#                                 password=user.password,
#                                 schoolId=user.schoolid,
#                                 sckey=user.sckey)
#
#
# @app.post('/updatecourseid')
# async def update_courseid(user: User) -> dict:
#     """
#     更新课程ID
#     @param user:
#     @return:
#     """
#     return await cloud_sign.run(username=user.username,
#                                 password=user.password,
#                                 schoolId=user.schoolid,
#                                 sckey=user.sckey,
#                                 task_type='update')


if __name__ == "__main__":
    # uvicorn.run(app, host="127.0.0.1", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=9090)
