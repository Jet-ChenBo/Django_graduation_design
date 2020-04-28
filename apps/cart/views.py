from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection


# /cart/add
class CartAddView(View):
    '''
    添加商品到购物车
    前端通过 ajax post 请求
    '''
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res':0., 'errmsg':'请先登录'})

        # 接受数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res':1, 'errmsg':'数据不完整'})
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res':2, 'errmsg':'商品数目出错'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res':3, 'errmsg':'商品不存在'})

        # 业务处理：添加购物车
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 1.查看用户购物车是否已经存在相同的商品,如果查不到会返回None
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            # 累加购物车中商品的数目
            count += int(cart_count)
        # 2.查看商品库存是否足够
        if count>sku.stock:
            return JsonResponse({'res':4, 'errmsg':'商品库存不足'})
        # 3.添加购物车
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车中商品的条目数
        total_count = conn.hlen(cart_key)

        # 返回应答
        return JsonResponse({'res':5, 'msg':'添加成功', 'total_count':total_count})


