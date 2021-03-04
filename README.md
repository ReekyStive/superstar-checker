# Superstar Checker

这是一个从 [mkdir700/chaoxing_auto_sign](https://github.com/mkdir700/chaoxing_auto_sign) Fork 过来的经过修改版本。此版本阉割了 API 和健康打卡，仅保留了本地版本。

## 如果你不想折腾

这里有为 Windows 打包好的版本，开箱即用。

[checker-win.7z](https://github.com/ReekyStive/superstar-checker/releases/download/v1.0/checker-win.7z)

其中包含

- 本项目源代码
- Python 解释器
- 依赖包

## 功能描述

- 登录方式

    支持手机号码登录和学号登录

- 定时签到

    支持固定时间间隔签到和指定时间点签到

- 签到功能

    支持普通签到，手势签到，二维码签到，位置签到，拍照签到
    支持自定义拍照签到照片及地理位置信息

- 微信推送

    配置 server 酱 `sckey` 后，签到消息可以推送至您的个人微信

## 项目目录

``` shell
├── config.py          # 配置文件
├── image
│   └── placeholder    # 占位文件，使用拍照签到需要删除此文件并添加图片文件
├── log.py
├── main.py            # 主程序
├── readme.md
└── requirements.txt
```

## 使用方法

运行 `checker.py` 可以立即执行一次签到，一般用于测试

运行 `scheduler.py` 启动定时器，在到达指定时间时执行签到

``` bash
$ cd superstar-checker
# 进入项目文件夹

$ python3 -m pip install -r requirements.txt
# 安装依赖

$ vim config.py
# 编辑配置，可以使用自己喜欢的编辑器

$ python3 main.py
# 运行主程序
```

### 拍照签到说明

将需要上传的图片文件放到 `image` 文件夹中，可以放多张图片

遇到拍照签到时，会随机抽取一张进行上传，如果 `image` 下没有图片，会上传原作者拍的一张照片

### 关于 `schoolid`

如果是学号登录，有一个额外的**必填**参数 `schoolid`，下面是获取方法

进入 [`https://passport2.chaoxing.com/login`](https://passport2.chaoxing.com/login)，根据下面的动图演示找到 `schoolid`

![tutorial.gif](http://cdn.z2blog.com/2020/04/15/cdf5a0415014614.gif)

## 其他签到脚本推荐

| 项目地址 | 开发语言 | 备注 |
| - | - | - |
| [mkdir700/chaoxing_auto_sign](https://github.com/mkdir700/chaoxing_auto_sign) | Python | 本项目的原版本，支持 API 和健康打卡 |
| [PrintNow/ChaoxingSign](https://github.com/PrintNow/ChaoxingSign) | PHP | PHP 版超星自动签到，支持多用户，二次开发便捷 |
| [Wzb3422/auto-sign-chaoxing](https://github.com/Wzb3422/auto-sign-chaoxing) | TypeScript | 超星学习通自动签到，梦中刷网课 |
| [Huangyan0804/AutoCheckin](https://github.com/Huangyan0804/AutoCheckin) | Python | 学习通自动签到，支持手势，二维码，位置，拍照等 |
| [aihuahua-522/chaoxing-testforAndroid](https://github.com/aihuahua-522/chaoxing-testforAndroid) | Java | 超星学习通自动签到 |
| [yuban10703/chaoxingsign](https://github.com/yuban10703/chaoxingsign) | Python | 超星学习通自动签到 |
