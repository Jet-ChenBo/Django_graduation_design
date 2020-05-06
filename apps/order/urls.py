from django.conf.urls import url
from order import views

urlpatterns = [
    url(r'^submit$', views.OrderSubmitView.as_view(), name='submit'),  # 提交订单页面的显示
]