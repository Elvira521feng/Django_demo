from django.conf.urls import url
from orders import views

urlpatterns = [
    url(r'^orders/settlement/$', views.OrdersSettlementView.as_view()),
    url(r'^orders/$', views.OrdersView.as_view()),
]