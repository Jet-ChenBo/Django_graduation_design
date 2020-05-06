from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings
from goods.models import GoodsSKU
from user.models import Address
from order.models import OrderInfo,OrderGoods
from django_redis import get_redis_connection
from util.mixin import LoginRequiredMixmin
from datetime import datetime
import os


# /order/submit
class OrderSubmitView(LoginRequiredMixmin, View):
    '''提交订单页面显示'''
    def post(self, request):
        user = request.user
        # 获取参数
        sku_ids = request.POST.getlist('sku_ids')
        # 校验参数
        if not sku_ids:
            # 跳转到购物车界面
            return redirect(reverse('cart:show'))

        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        skus = []
        total_count = 0  # 保存商品的总件数和总价格
        total_price = 0

        # 遍历sku_ids获取用户要购买的商品的信息
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取用户所购买的商品的数量
            count = conn.hget(cart_key, sku_id)
            # 计算商品的小计
            amount = sku.price * int(count)
            # 动态增加商品的属性
            sku.count = int(count)
            sku.amount = amount
            # 累加商品的总件数和价格
            total_count += int(count)
            total_price += amount

            skus.append(sku)

        # 运费
        transit_price = 20

        # 实付款
        total_pay = total_price + transit_price

        # 获取用户的收件地址
        address = Address.objects.filter(user=user)

        # 获取用户购买的商品的id字符串
        sku_ids = ','.join(sku_ids)

        # 组织上下文
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_price': total_price,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'address': address,
            'sku_ids': sku_ids
        }

        return render(request, 'submit_order.html', context)



