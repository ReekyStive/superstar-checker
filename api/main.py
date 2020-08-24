import uvicorn
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import cloud_sign

app = FastAPI()


class User(BaseModel):
    username: str
    password: str
    schoolid: Optional[str] = None
    sckey: Optional[str] = None


@app.get('/sign')
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
    return await cloud_sign.run(username=username,
                                password=password,
                                schoolId=schoolid,
                                sckey=sckey)


@app.get('/updatecourseid')
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
    return await cloud_sign.run(username=username,
                                password=password,
                                schoolId=schoolid,
                                sckey=sckey,
                                task_type='update')


@app.post('/sign')
async def sign(user: User) -> dict:
    """
    签到
    @param user:
    @return:
    """
    return await cloud_sign.run(username=user.username,
                                password=user.password,
                                schoolId=user.schoolid,
                                sckey=user.sckey)


@app.post('/updatecourseid')
async def update_courseid(user: User) -> dict:
    """
    更新课程ID
    @param user:
    @return:
    """
    return await cloud_sign.run(username=user.username,
                                password=user.password,
                                schoolId=user.schoolid,
                                sckey=user.sckey,
                                task_type='update')


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
