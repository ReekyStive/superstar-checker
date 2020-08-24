## 功能描述

- 登录方式：

支持手机号码登录和学号登录

- 签到功能：

健康打卡：

支持腾讯云函数，设置定时触发自动打卡

详情： https://github.com/mkdir700/chaoxing_auto_sign/tree/latest/heath

课程签到：

支持普通签到，手势签到，二维码签到，位置签到，拍照签到

支持自定义拍照签到照片及地理位置信息

- 微信推送：

配置server酱key后，签到消息可以推送至您的个人微信

- 接口部署：

使用FastApi框架 和 MongoDB数据库，可以将此项目部署到服务器，通过接口实现多用户多任务签到



## 项目目录

```
├── api                         # 课堂签到（API）
│   ├── cloud_sign.py
│   ├── config.py
│   ├── db_handler.py
│   ├── main.py
│   ├── readme.md
│   ├── requirements.txt
│   └── sign_script.py
├── heath                       # 健康日报
│   ├── main.py
│   └── readme.md
├── local                       # 课程签到（本地）
│   ├── config.py
│   ├── image
│   │   └── 深度截图_选择区域_20200522103426.png
│   ├── local_sign.py
│   ├── log.py
│   ├── logs.log
│   └── requirements.txt
├── __pycache__
├── readme.md
└── start.sh
```

- 多人使用：

需要**部署api**，供自己和其他人使用，可以选择`api`下的脚本

部署参考文章：

https://github.com/mkdir700/chaoxing_auto_sign/blob/master/api/readme.md

- 个人使用：

本地运行，可以选择`local`下的脚本

拍照签到说明：

【本地版】可以自定义拍照签到的上传图片

【Api版】暂时不支持自定义图片，默认【拍照签到】是一张黑色图片

本地版，自定义图片方法

将需要上传的图片文件，放到`image`文件夹中即可，可以放多张图片

遇到拍照签到时，会默认随机抽取一张进行上传，如果`image`下没有图片，默认上传我自己拍摄的一张照片 2333~


## 不想折腾？

现有接口请求之后，要等一段时间才能开始签到，具体等多久只能看当时同时请求的人有多少了，一般都比较慢。如果有条件的话，建议选择本地脚本，或者自己部署个api脚本。

每次需要签到的时候，就在浏览器内访问这个链接

`{}`替换成自己的账号密码

`http://101.89.182.58:9090/sign?username={}&password={}&schoolid=&sckey=`



## 接口使用

```
http://101.89.182.58:9090/sign
```

温馨提示：

接口目前使用人数过多，所以有环境能自己搭建，尽量使用自己搭建的

人数过多，会出现签到不及时的现象

请求代码示例：
```python
import requests

# POST
params = {
    'username': 'xxxxx',
    'password': 'xxxxx',
    'schoolid': '',
    'sckey': ''
}
requests.post('http://101.89.182.58:9090/sign', params=params)

# GET
username = 'xxx'
password = 'xxx'
requests.get('http://101.89.182.58:9090/sign?username={}&password={}'.format(username, password))
```

在线接口调试：

<http://101.89.182.58:9090/docs#/default/sign_sign_get>


| 请求方式 |   参数   |  说明  | 是否必须 |
| :------: | :------: | :----: | :------: |
|          | username |  账号  |    是    |
|   **POST/GET**   | password |  密码  |    是    |
|          | schoolid | 学校ID |    否    |
| | sckey | server酱key | 否 |


**如果是学号登录，fid参数必填**

### 如何获取FID
关于学号登录方式，有一个额外参数`schoolid`

http://passport2.chaoxing.com/login

动图演示：

![2020/04/15/cdf5a0415014614.gif](http://cdn.z2blog.com/2020/04/15/cdf5a0415014614.gif)


## 其他签到脚本推荐


| 项目地址                                                | 开发语言   | 备注                                           |
| ------------------------------------------------------- | ---------- | ---------------------------------------------- |
| https://github.com/PrintNow/ChaoxingSign                | PHP        | PHP版超星自动签到，支持多用户，二次开发便捷！|
| https://github.com/Wzb3422/auto-sign-chaoxing           | TypeScript | 超星学习通自动签到，梦中刷网课       |
| https://github.com/Huangyan0804/AutoCheckin             | Python     | 学习通自动签到，支持手势，二维码，位置，拍照等 |
| https://github.com/aihuahua-522/chaoxing-testforAndroid | Java       | 学习通（超星）自动签到               |
| https://github.com/yuban10703/chaoxingsign              | Python     | 超星学习通自动签到                   |
