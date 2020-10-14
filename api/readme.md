## TODO

- 增加请求频率限制

- 优化后台任务执行效率

- 优化微信推送功能

## 环境：

python3.7 , mongodb

## screen

### 安装

centos

```
yum install screen
```



debian,ubuntu

```
apt-get install screen
```



### 进入

创建一个窗口，指令如下

```
screen -S fastapi
```

然后就进入了一个全新的窗口



## 克隆项目

在合适的目录下

```
git clone https://github.com/mkdir700/chaoxing_auto_sign.git
```

![2020/04/15/7a5e50415034311.png](http://cdn.z2blog.com/2020/04/15/7a5e50415034311.png)



## 安装模块

在服务器部署api进入api文件夹

![2020/04/15/b23370415033300.png](http://cdn.z2blog.com/2020/04/15/b23370415033300.png)



使用包管理工具`pip`安装所需模块

```
pip install -r requirements.txt
```



## 运行程序

```
uvicorn main:app --host 0.0.0.0 --port 9090
```

访问`ip:9090`即可访问

![2020/04/15/91c570415033540.png](http://cdn.z2blog.com/2020/04/15/91c570415033540.png)



## 切换回主窗口

程序就一样一直挂就行了，但是我们可能还要进行其他操作

按`Ctrl + A + D` 可切换回之前的主窗口



## 关闭程序

关闭程序，我们需要切换到程序运行窗口

```
screen -r fastapi
```

然后按`Ctrl + C`结束



## 温馨提示：

1. 如果您的服务器是腾讯云或者阿里云，部署后无法签到，原因是学习通的服务器屏蔽了这两家服务商的ip
2. 如果你所在服务商有安全组规则，请将访问端口设置到安全组(如果安装了宝塔，也需要在宝塔放行访问端口)
3. 部署python程序，建议使用虚拟环境，在虚拟环境中，操作上述步骤，详情python虚拟环境请百度