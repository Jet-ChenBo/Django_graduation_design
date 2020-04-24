from django.contrib import admin
from goods.models import GoodsType, GoodsSKU, Goods, IndexTypeGoodsBanner, IndexGoodsBanner
# Register your models here.

class GoodsSKUAdmin(admin.ModelAdmin):
    '''商品SKU管理类'''
    list_display = ['name','goods','type']  # 管理页面显示的字段
    list_filter = ['type']  # 过滤条件


class IndexTypeGoodsBannerAdmin(admin.ModelAdmin):
    '''分类商品展示管理类'''
    list_display = ['sku','type','display_type','index']
    list_filter = ['type']


class IndexGoodsBannerAdmin(admin.ModelAdmin):
    '''轮播商品管理类'''
    list_display = ['sku','index']


admin.site.register(GoodsType)
admin.site.register(Goods)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)