from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from areas import views

urlpatterns = [
    # url(r'^areas/$', views.AreasView.as_view(), name='areas-list'),
    # url(r'^areas/(?P<pk>\d+)/$', views.SubAreasView.as_view(), name='areas-detail'),
]

router = DefaultRouter()
router.register('areas', views.AreaViewSet, base_name='areas')
urlpatterns += router.urls
