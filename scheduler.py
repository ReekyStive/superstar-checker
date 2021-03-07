from config import *
import checker
import schedule
from time import sleep

if __name__ == '__main__':
    if fixed_interval:
        seconds = exec_interval['hour'] * 3600 + \
            exec_interval['minute'] * 60 + exec_interval['second']
        schedule.every(seconds).seconds.do(checker.run)
        print('已开启定时执行, 每间隔 [ {} 时 {} 分 {} 秒] 执行一次签到任务'.format(
              exec_interval['hour'], exec_interval['minute'], exec_interval['second']))
    else:
        for item in exec_times:
            schedule.every().day.at(item).do(checker.run)
        print('已开启定时执行, 将在指定的时间点执行签到任务')
    while True:
        schedule.run_pending()
        sleep(1)
