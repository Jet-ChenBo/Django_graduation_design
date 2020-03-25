from django.shortcuts import render
from django.views.generic import View
import re
from user.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings

# Create your views here.

# /user/register
class RegisterView(View):
    '''注册页面'''
    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''注册的处理'''
        # 接收前端传来的数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        cpassword = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 数据校验
        if not all((username, password, cpassword, email)):
            return render(request, 'register.html', {'errmsg':'数据不完整'})

        if password != cpassword:
            return render(request, 'register.html', {'errmsg': '两次密码不一致'})

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请您同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except Exception:
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 往数据库添加数据
        user = User.objects.create_user(username, password, email)
        user.is_active = 0  # 初始状态未激活，需要到邮箱验证激活
        user.save()

        # 发送激活用户账号的邮件, /user/active/用户id（需要加密）
        # 加密id
        serilalizer = Serializer(settings.SECRET_KEY, 3600)
        info = {'id': user.id}
        token = serilalizer.dumps(info)  # 加密，返回的是加密后的byte字符串
        token = token.decode('utf-8')
        # 发送邮件

