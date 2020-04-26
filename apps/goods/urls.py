
from django.conf.urls import url
from goods import views

urlpatterns = [
    url(r'^index$', views.IndexView.as_view(), name='index'),  # 首页
    url(r'^goods/(?P<goods_id>\d+$)', views.DetailView.as_view(), name='detail'),  # 详情页
]