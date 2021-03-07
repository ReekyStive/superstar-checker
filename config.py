# ================= 配置区 start ===================

# 学习通账号密码, 可添加多个账号
user_infos = [
    {
        'username': 'xxxx',
        'password': 'xxxx',
        'schoolid': ''  # 学号登录才需要填写
    }
]

# fixed_interval: 是否使用固定时间间隔
# 为 True 则使用 exec_interval 中的配置, 为 False 则使用 exec_times 中的配置
# 为 True 则每隔固定时间执行一次, 默认 5 分钟, 为 False 则在固定时间点执行
fixed_interval = True
exec_interval = {
    'hour': 0, 'minute': 5, 'second': 0
}
exec_times = [
    '08:00',
    '08:10',
    '18:00'
]

# server 酱
server_chan_sckey = 'xxxx'  # 申请地址 http://sc.ftqq.com/3.version
server_chan = {
    'status': False,  # 如果关闭 server 酱功能，请改为 False
    'url': 'https://sc.ftqq.com/{}.send'.format(server_chan_sckey)
}

# 学习通账号 cookies 缓存文件路径
cookies_path = "./"
cookies_file_path = cookies_path + "cookies.json"

# activeid 保存文件路径
activeid_path = "./"
activeid_file_path = activeid_path + "activeid.json"

# 拍照签到的图片文件
image_path = "./image/"

# 位置信息
latitude = "-2"
longitude = "-1"

# ip 地址
clientip = "0.0.0.0"

# 状态码
status_code_dict = {
    1000: '登录成功',
    1001: '登录信息有误',
    1002: '拒绝访问',
    2000: '当前暂无签到任务',
    2001: '有任务且签到成功',
    4000: '未知错误'
}
# ================= 配置区 end ===================
