from celery import Celery
from django.core.mail import send_mail
from django.conf import settings
from django.template import loader, RequestContext

# 因任务处理者也是用这段代码，所以需要添加环境变量
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshdelivery.settings')
django.setup()

# 创建一个Celery的实力对象，第一个参数可随便写，第二个参数指定用redis作为broker，用第8个数据库
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')

# 创建任务函数
@app.task  # 装饰器将任务注册到broker的队列中。
def send_register_active_emali(to_email, username, token):
    '''发送激活邮件'''
    subject = '生鲜配送账号激活'  # 主题
    message = ''  # 正文，不能传html标签
    sender = settings.EMAIL_FROM  # 发送者
    receiver = [to_email]  # 收件人邮箱
    html_message = '''
                           <h1>%s,恭喜您成功注册生鲜配送账号</h1>请点击下面的链接激活您的账户</br>
                           <a href="http:127.0.0.1:8000/user/active/%s">激活账户</a>
                          ''' % (username, token)  # 正文，可以传html标签
    send_mail(subject, message, sender, receiver, html_message=html_message)