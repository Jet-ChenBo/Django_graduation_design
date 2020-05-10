from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.generic import View
from goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, GoodsSKU
from order.models import OrderGoods
from django_redis import get_redis_connection
from django.core.paginator import Paginator

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


# /list/type_id/page?sort=**
class ListView(View):
    '''商品列表页'''
    def get(self, request, type_id, page):
        # 获取商品分类信息
        types = GoodsType.objects.all()

        # 获取当前种类信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 获取当前排序方式，有三种：default(id)、price、hot(sales)
        sort = request.GET.get('sort')

        # 按照排序方式获得当前分类的所有商品
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # todo:分页
        paginator = Paginator(skus, 4)  # 每页四个商品

        # 获取第page页的实例对象
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        skus_page = paginator.page(page)

        # todo:进行页码控制，最多显示5个页码
        num_pages = paginator.num_pages
        if num_pages <= 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 获取用户购物车中商品的数量
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context = {
            'types':types,
            'type': type,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'pages': pages,
            'sort': sort
        }

        return render(request, 'list.html', context)