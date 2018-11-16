from django.conf.urls import url
from oauth import views

urlpatterns = [
    url('^qq/authorizations/$', views.QQAuthURLView.as_view()),
    url(r'^qq/user/$', views.QQAuthUserView.as_view()),
]