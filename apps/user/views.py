from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
import re
from user.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from celery_tasks.tasks import send_register_active_emali
from django.urls import reverse
from django.contrib.auth import authenticate, logout, login
from user.models import User, Address
from goods.models import GoodsSKU
from order.models import OrderGoods, OrderInfo
from django_redis import get_redis_connection
from util.mixin import LoginRequiredMixmin

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
        username = request.POST.get('user_name')
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
        user = User.objects.create_user(username, email, password)
        user.is_active = 0  # 初始状态未激活，需要到邮箱验证激活
        user.save()

        # 发送激活用户账号的邮件, /user/active/用户id（需要加密）
        # 加密id
        serilalizer = Serializer(settings.SECRET_KEY, 3600)
        info = {'id': user.id}
        token = serilalizer.dumps(info)  # 加密，返回的是加密后的byte字符串
        token = token.decode('utf-8')
        # 发送邮件
        send_register_active_emali.delay(email, username, token)  # 发出任务
        # 返回应答
        return HttpResponse('注册成功，请到邮箱中激活您的账号')


# /user/active/加密token
class ActiveView(View):
    '''用户激活账号'''
    def get(self, request, token):
        # 解密获取用户id
        serilalizer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serilalizer.loads(token)
            user_id = info['id']
            # 获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse('激活链接已过期')


# /user/login
class LoginView(View):
    '''登录'''
    def get(self, request):
        '''显示登录页面'''
        # 检查用户上次是否点击了记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username':username, 'checked':checked})

    def post(self, request):
        '''登录校验'''
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remember')

        if not all((username, password)):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 用户认证
        user = authenticate(username = username, password=password)
        if user is not None:
            # 认证成功
            if user.is_active:
                login(request, user)
                # 获取登录后要跳转的网页，默认为首页
                next_url = request.GET.get('next', reverse('goods:index'))
                # 是否记住用户名
                response = redirect(next_url)
                if remember == 'on':
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response
            else:
                return render(request, 'login.html', {'errmsg': '用户未激活'})
        else:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


# /user/logout
class LogoutView(View):
    '''退出登录'''
    def get(self, requset):
        # 退出登录，清除用户的session信息
        logout(requset)
        # 跳转到首页
        return redirect(reverse('goods:index'))


# /user
class UserInfoView(LoginRequiredMixmin, View):
    '''用户中心-信息页'''
    def get(self, request):
        '''显示'''
        # 获取用户个人信息
        user = request.user

        # 获取用户历史浏览记录
        #sr = StrictRedis(db=9)
        con = get_redis_connection('default')  # default对应缓存配置中的键名
        history_key = "history_%d" % user.id

        # 获取历史浏览记录前五个商品的id
        sku_ids = con.lrange(history_key, 0, 4)

        # 从数据库中查询商品的具体信息
        # 数据库查询是至上而下的，所以就不能保持原来的顺序，例如[2,3,1],用filter查出来是[1,2,3]
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        context = {'page':'info',
                   'goods_li':goods_li
                    }
        return render(request, 'user_center_info.html', context)


# /user/site
class UserSiteView(LoginRequiredMixmin, View):
    '''用户中心-地址页'''
    def get(self, request):
        # 获取用户默认收获地址
        user = request.user
        address = Address.objects.get_default_address(user)
        return render(request, 'user_center_site.html', {'page':'site','address':address})