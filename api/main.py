import os
from fastapi import FastAPI, BackgroundTasks
from cloud_sign import *

app = FastAPI()


@app.post('/sign')
@app.get('/sign')
async def sign(*, username: str, password: str, schoolid=None, sckey=None,
               background_tasks: BackgroundTasks):
    USER_INFO = {}
    USER_INFO['username'] = username
    USER_INFO['password'] = password
    USER_INFO['schoolid'] = schoolid
    background_tasks.add_task(interface, USER_INFO, sckey)
    return {'message': '您的请求已收到,签到任务正在排队进行中'}