from django.contrib import admin
from goods.models import GoodsType, GoodsSKU, Goods, IndexTypeGoodsBanner, IndexGoodsBanner
from django.core.cache import cache
from celery_tasks.tasks import generate_static_index_html
# Register your models here.


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 发出任务，让celery worker生成静态页面
        generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete('index_page_data')


    def delete_model(self, request, obj):
        super().delete_model(request, obj)

        # 发出任务，让celery worker生成静态页面
        generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete('index_page_data')


class GoodsSKUAdmin(admin.ModelAdmin):
    '''商品SKU管理类'''
    list_display = ['name','goods','type']  # 管理页面显示的字段
    list_filter = ['type']  # 过滤条件


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    '''分类商品展示管理类'''
    list_display = ['sku','type','display_type','index']
    list_filter = ['type']


class IndexGoodsBannerAdmin(BaseModelAdmin):
    '''轮播商品管理类'''
    list_display = ['sku','index']


class GoodsTypeAdmin(BaseModelAdmin):
    pass



admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(Goods)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)