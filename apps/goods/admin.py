from django.contrib import admin
from goods.models import GoodsType, GoodsSKU, Goods, IndexTypeGoodsBanner, IndexGoodsBanner
# Register your models here.

class IndexTypeGoodsBannerAdmin(admin.ModelAdmin):
    '''分类商品展示管理类'''
    list_display = ['sku','type','display_type','index']  # 管理页面显示的字段
    list_filter = ['type']  # 过滤条件

admin.site.register(GoodsType)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)