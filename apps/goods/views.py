from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.generic import View
from goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, GoodsSKU
from order.models import OrderGoods
from django_redis import get_redis_connection

# /index
class IndexView(View):
    '''首页'''
    def get(self, request):
        # 获取商品的种类信息
        types = GoodsType.objects.all()

        # 获取首页轮播商品信息
        goods_banners = IndexGoodsBanner.objects.all().order_by('index')

        # 获取首页分类商品展示信息
        for type in types:
            # 获取type种类首页分类商品的图片展示信息
            image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
            # 获取type种类首页分类商品的文字展示信息
            title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

            # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
            type.image_banners = image_banners
            type.title_banners = title_banners

        # 获取用户购物车中商品的数量
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context = {
            'types': types,
            'goods_banners': goods_banners,
            'cart_count' : cart_count
        }

        return render(request, 'index.html', context)


# /goods/sku_id
class DetailView(View):
    '''详情页'''
    def get(self, request, goods_id):
        '''显示详情页'''
        # 获取商品
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods：index'))

        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[0:2]

        # 获取用户购物车中商品的数量
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            # 添加用户的历史浏览记录
            # 1.移除已经浏览过的重复的商品,没有的话不会报错
            history_key = 'history_%d' % user.id
            conn.lrem(history_key,0,goods_id)
            # 2.存储历史浏览记录，左侧插入
            conn.lpush(history_key, goods_id)
            # 3.只保存五条
            conn.ltrim(history_key,0,4)


        # 组织模板上下文
        context = {
            'sku': sku,
            'types': types,
            'sku_orders': sku_orders,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'all_comment': len(sku_orders),
        }

        return render(request, 'detail.html', context)