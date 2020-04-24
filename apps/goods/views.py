from django.shortcuts import render
from django.views.generic import View
from goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner

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

        # 组织模板上下文
        context = {
            'types': types,
            'goods_banners': goods_banners,
        }

        return render(request, 'index.html', context)