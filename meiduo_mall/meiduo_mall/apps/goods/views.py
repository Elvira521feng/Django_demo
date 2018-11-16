from django.shortcuts import render
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_haystack.viewsets import HaystackViewSet

from goods.models import SKU
from goods.serializers import SKUSerializer, SKUIndexSerializer


# Create your views here.

# /skus/search/?text=<搜索关键字>
class SKUSearchViewSet(HaystackViewSet):
    """商品搜索视图"""
    # 指定索引模型类
    index_models = [SKU]

    # 指定搜索结果序列化时所使用的序列器类
    # 搜索结果中包含两个字段:
    # text: 索引字段
    # object: 搜索出模型对象
    serializer_class = SKUIndexSerializer


# 1）获取某个第三级分类id下的所有商品的信息。
# 2）分页&排序。


# GET /categories/(?P<category_id>\d+)/skus/
class SKUListView(ListAPIView):
    serializer_class = SKUSerializer
    # queryset = SKU.objects.filter(category_id=category_id, is_launched=True)

    # 排序
    filter_backends = [OrderingFilter]
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        """指定当前视图所使用的查询集"""
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)

    # def get(self, request, category_id):
    #     """
    #     self.kwargs: 保存从url地址中提取所有命名参数
    #     获取分类商品的数据:
    #     1. 根据`category_id`查询分类商品的数据
    #     2. 将分类商品的数据序列化并返回
    #     """
    #     # 1. 根据`category_id`查询分类商品的数据
    #     # skus = SKU.objects.filter(category_id=category_id, is_launched=True)
    #     skus = self.get_queryset()
    #
    #     # 2. 将分类商品的数据序列化并返回
    #     serializer = self.get_serializer(skus, many=True)
    #     return Response(serializer.data)
