from django.contrib import admin
from goods.models import GoodsType, GoodsSKU, Goods, IndexTypeGoodsBanner, IndexGoodsBanner
# Register your models here.

admin.site.register(GoodsType)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexTypeGoodsBanner)