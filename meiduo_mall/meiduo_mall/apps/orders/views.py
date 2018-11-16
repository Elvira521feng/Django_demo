from decimal import Decimal
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from goods.models import SKU
from orders.serializers import OrderSKUSerializer, OrderSettlementSerializer, OrderSerializer


# Create your views here.


# POST /orders/
class OrdersView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    # def post(self, request):
    #     """
    #     提交订单数据保存(订单创建):
    #     1. 获取参数并进行校验(完整性，地址是否存在，支付方式是否合法)
    #     2. 保存提交的订单数据
    #     3. 返回应答，订单保存成功
    #     """
    #     # 1. 获取参数并进行校验(完整性，地址是否存在，支付方式是否合法)
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 2. 保存提交的订单数据(create)
    #     serializer.save()
    #
    #     # 3. 返回应答，订单保存成功
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


# GET /orders/settlement/
class OrdersSettlementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        登录用户结算商品数据获取:
        1. 从redis用户购物车数据中获取被勾选的商品sku_id和对应数量count
        2. 根据商品id获取对应商品的信息，组织运费
        3. 序列化数据并返回
        """
        # 1. 从redis用户购物车数据中获取被勾选的商品sku_id和对应数量count
        redis_conn = get_redis_connection('cart')

        # 从redis的set中获取被勾选商品的sku_id
        user = request.user
        cart_selected_key = 'cart_selected_%s' % user.id

        # (b'<sku_id>', b'<sku_id>', ...)
        sku_ids = redis_conn.smembers(cart_selected_key)

        # 从redis的hash中获取用户购物车中所有商品sku_id和对应数量count
        cart_key = 'cart_%s' % user.id

        # {
        #     b'<sku_id>': b'<count>',
        #     ...
        # }
        cart_dict = redis_conn.hgetall(cart_key)

        # 组织数据
        cart = {}
        # {
        #     '<sku_id>': '<count>',
        #     ...
        # }
        for sku_id, count in cart_dict.items():
            cart[int(sku_id)] = int(count)

        # 2. 根据商品id获取对应商品的信息，组织运费
        skus = SKU.objects.filter(id__in=sku_ids)

        for sku in skus:
            # 给sku对象增加属性count，保存用户所要结算的该商品数量count
            sku.count = cart[sku.id]

        # 组织运费
        freight = Decimal(10)

        # 3. 序列化数据并返回
        # serializer = OrderSKUSerializer(skus, many=True)
        #
        # resp_data = {
        #     'freight': freight,
        #     'skus': serializer.data
        # }
        #
        # return Response(resp_data)

        # 组织数据
        res_dict = {
            'freight': freight,
            'skus': skus
        }

        serializer = OrderSettlementSerializer(res_dict)
        return Response(serializer.data)
