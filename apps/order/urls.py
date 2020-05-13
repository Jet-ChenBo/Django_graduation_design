from django.conf.urls import url
from order import views

urlpatterns = [
    url(r'^submit$', views.OrderSubmitView.as_view(), name='submit'),  # 提交订单页面的显示
    url(r'^commit$', views.OrderCommitView.as_view(), name='commit'),  # 创建订单
    url(r'^pay$', views.OrderPayView.as_view(), name='pay'),  # 订单支付
    url(r'^check$', views.CheckPayView.as_view(), name='check'),  # 查询订单支付结果
    url(r'^comment/(?P<order_id>.+)$', views.CommentView.as_view(), name='comment'),  # 商品评论
]