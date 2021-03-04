from config import *
import checker
from apscheduler.schedulers.blocking import BlockingScheduler

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    if fixed_interval:
        scheduler.add_job(checker.run, 'interval', hours=exec_interval['hour'],
                          minutes=exec_interval['minute'], seconds=exec_interval['second'])
        print('已开启定时执行, 每间隔 [ {} 时 {} 分 {} 秒] 执行一次签到任务'.format(
              exec_interval['hour'], exec_interval['minute'], exec_interval['second']))
    else:
        for item in exec_times:
            scheduler.add_job(checker.run, 'cron', hour=item['hour'],
                              minute=item['minute'], second=item['second'])
        print('已开启定时执行, 将在指定的时间点执行签到任务')
    scheduler.start()
