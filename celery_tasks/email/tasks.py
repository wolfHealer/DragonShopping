
# 生产者 -- 任务，函数
# 1. 这个函数 必须要让celery的实例的 task装饰器 装饰
# 2. 需要celery 自动检测指定包的任务
from django.core.mail import send_mail
from celery_tasks.main import app

@app.task
def celery_send_email(subject,message,from_email,recipient_list,html_message):

    send_mail(subject=subject,
              message=message,
              from_email=from_email,
              recipient_list=recipient_list,
              html_message=html_message)