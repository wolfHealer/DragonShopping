# 生产者 -- 任务，函数
# 1. 这个函数 必须要让celery的实例的 task装饰器 装饰
# 2. 需要celery 自动检测指定包的任务

from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
def celery_send_sms_code(mobie,code):

    CCP().send_template_sms(mobie,[code,5],1)
