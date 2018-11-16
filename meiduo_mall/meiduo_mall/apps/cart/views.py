import base64
import pickle

from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart import constants
from cart.serializers import CartSerializer, CartSKUSerializer, CartDelSerializer, CartSelectAllSerializer
from goods.models import SKU

# Create your views here.


#  PUT /cart/selection/
class CartSelectAllView(APIView):
    def perform_authentication(self, request):
        """让当前跳过DRF的认证过程"""
        pass

    def put(self, request):
        """
        购物车记录全选和取消全选:
        1. 获取参数并进行校验(selected)
        2. 获取user并进行处理
        3. 购物车记录全选和取消全选
            3.1 如果用户已登录，操作redis中购物车记录
            3.2 如果用户未登录，操作cookie中购物车记录
        4. 返回应答
        """
        # 1. 获取参数并进行校验(selected)
        serializer = CartSelectAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取数据
        selected = serializer.validated_data['selected']

        # 2. 获取user并进行处理
        try:
            # 调用request.user会触发DRF的认证，在这里如果认证处理，可以自己进行处理
            user = request.user
        except Exception:
            user = None

        # 3. 购物车记录全选和取消全选
        if user is not None and user.is_authenticated:
            # 3.1 如果用户已登录，操作redis中购物车记录
            redis_conn = get_redis_connection('cart')

            # 获取redis用户购物车中添加的所有商品id hash
            cart_key= 'cart_%s' % user.id
            # hkeys(key): 获取redis中hash所有的属性
            sku_ids = redis_conn.hkeys(cart_key)

            # 全选和取消全选
            cart_selected_key = 'cart_selected_%s' % user.id
            if selected:
                # 全选
                # sadd(key, *members): 将set集合添加元素，不需要关注元素是否重复
                redis_conn.sadd(cart_selected_key, *sku_ids)
            else:
                # 取消全选
                # srem(key, *members): 从set集合移除元素，有则移除，无则忽略
                redis_conn.srem(cart_selected_key, *sku_ids)

            return Response({'message': 'OK'})
        else:
            response =  Response({'message': 'OK'})
            # 3.2 如果用户未登录，操作cookie中购物车记录
            cookie_cart = request.COOKIES.get('cart')  # None

            if cookie_cart is None:
                return response

            # 解析cookie中的购物车数据
            # {
            #     '<sku_id>': {
            #         'count': '<count>',
            #         'selected': '<selected>',
            #     },
            #     ...
            # }
            cart_dict = pickle.loads(base64.b64decode(cookie_cart)) # {}

            if not cart_dict:
                return response

            # 全选和取消全选
            for sku_id in cart_dict:
                cart_dict[sku_id]['selected'] = selected

            # 4. 返回应答
            # 设置购物车cookie数据
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()  # str
            response.set_cookie('cart', cart_data, max_age=constants.CART_COOKIE_EXPIRES)
            return response


# /cart/
class CartView(APIView):
    def perform_authentication(self, request):
        """让当前跳过DRF的认证过程"""
        pass

    def delete(self, request):
        """
        购物车记录删除:
        1. 获取参数并进行校验(sku_id必传，sku_id对应的商品是否存在)
        2. 获取user并进行处理
        3. 删除用户的购物车记录
            3.1 如果用户已登录，删除redis中的购物车记录
            3.2 如果用户未登录，删除cookie中的购物车记录
        4. 返回应答，购物车记录删除成功
        """
        # 1. 获取参数并进行校验(sku_id必传，sku_id对应的商品是否存在)
        serializer = CartDelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取参数
        sku_id = serializer.validated_data['sku_id']

        # 2. 获取user并进行处理
        try:
            # 调用request.user会触发DRF的认证，在这里如果认证处理，可以自己进行处理
            user = request.user
        except Exception:
            user = None

        # 3. 删除用户的购物车记录
        if user is not None and user.is_authenticated:
            # 3.1 如果用户已登录，删除redis中的购物车记录
            redis_conn = get_redis_connection('cart')

            # 从redis中删除用户购物车记录中对应的商品的id和数量count  hash
            cart_key = 'cart_%s' % user.id

            pl = redis_conn.pipeline()

            # hdel(key, *fields): 删除redis中hash指定属性和值，有则删除，无则忽略
            pl.hdel(cart_key, sku_id)

            # 从redis中除用户购物车记录中对应的商品的勾选状态  set
            cart_selected_key = 'cart_selected_%s' % user.id
            # srem(key, *members): 从set集合移除元素，有则移除，无则忽略
            pl.srem(cart_selected_key, sku_id)

            pl.execute()

            # 返回应答
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT)
            # 3.2 如果用户未登录，删除cookie中的购物车记录
            cookie_cart = request.COOKIES.get('cart')  # None

            if cookie_cart is None:
                return response

            # 解析cookie中的购物车数据
            cart_dict = pickle.loads(base64.b64decode(cookie_cart))  # {}
            if not cart_dict:
                return response

            # 删除购物车记录
            if sku_id in cart_dict:
                del cart_dict[sku_id]
                # 重新设置购物车cookie数据
                cookie_data = base64.b64encode(pickle.dumps(cart_dict)).decode() # str
                response.set_cookie('cart', cookie_data, max_age=constants.CART_COOKIE_EXPIRES)

            # 4. 返回应答，购物车记录删除成功
            return response

    def put(self, request):
        """
        用户的购物车记录更新:
        1. 获取参数并进行校验(参数完整性，sku_id对应的商品是否存在，商品库存是否足够)
        2. 获取user并处理
        3. 更新用户的购物车记录
            3.1 如果用户已登录，更新redis中对应购物车记录
            3.2 如果用户未登录，更新cookie中对应购物车记录
        4. 返回应答，购物车记录更新成功
        """
        # 1. 获取参数并进行校验(参数完整性，sku_id对应的商品是否存在，商品库存是否足够)
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取参数
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count'] # 更新结果
        selected = serializer.validated_data['selected'] # 更新勾选状态

        # 2. 获取user并处理
        try:
            # 调用request.user会触发DRF的认证，在这里如果认证处理，可以自己进行处理
            user = request.user
        except Exception:
            user = None

        # 3. 更新用户的购物车记录
        if user is not None and user.is_authenticated:
            # 3.1 如果用户已登录，更新redis中对应购物车记录
            # 获取redis链接
            redis_conn = get_redis_connection('cart')

            # 在redis中更新对应sku_id商品的购物车数量count  hash
            cart_key = 'cart_%s' % user.id

            pl = redis_conn.pipeline()

            # hset(key, field, value): 将redis中hash的属性field设置值为value
            pl.hset(cart_key, sku_id, count)

            # 在redis中更新sku_id商品的勾选状态 set
            cart_selected_key = 'cart_selected_%s' % user.id

            if selected:
                # 勾选
                # sadd(key, *members): 将set集合添加元素，不需要关注元素是否重复
                pl.sadd(cart_selected_key, sku_id)
            else:
                # 取消勾选
                # srem(key, *members): 从set集合移除元素，有则移除，无则忽略
                pl.srem(cart_selected_key, sku_id)

            pl.execute()

            # 返回应答
            return Response(serializer.data)
        else:
            response = Response(serializer.data)
            # 3.2 如果用户未登录，更新cookie中对应购物车记录
            cookie_cart = request.COOKIES.get('cart')  # None

            if cookie_cart is None:
                return response

            # 解析cookie中的购物车数据
            cart_dict = pickle.loads(base64.b64decode(cookie_cart)) # {}
            if not cart_dict:
                return response

            # 更新用户购物车中sku_id商品的数量和勾选状态
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 4. 返回应答，购物车记录更新成功
            # 设置购物车cookie数据
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()  # str
            response.set_cookie('cart', cart_data, max_age=constants.CART_COOKIE_EXPIRES)
            return response

    def get(self, request):
        """
        购物车记录获取:
        1. 获取user
        2. 获取用户的购物车记录
            2.1 如果用户已登录，从redis中获取用户的购物车记录
            2.2 如果用户未登录，从cookie中获取用户的购物车记录
        3. 根据用户购物车中商品sku_id获取对应商品的信息
        4. 将商品数据序列化并返回
        """
        # 1. 获取user
        try:
            # 调用request.user会触发DRF的认证，在这里如果认证处理，可以自己进行处理
            user = request.user
        except Exception:
            user = None

        # 2. 获取用户的购物车记录
        if user is not None and user.is_authenticated:
            # 2.1 如果用户已登录，从redis中获取用户的购物车记录
            # 获取redis链接
            redis_conn = get_redis_connection('cart')

            # 从redis中获取用户购物车记录中商品的sku_id和对应数量count hash
            cart_key = 'cart_%s' % user.id
            # hgetall(key): 获取redis中hash的属性和值
            # {
            #     b'<sku_id>': b'<count>',
            #     ...
            # }
            redis_cart = redis_conn.hgetall(cart_key)

            # 从redis中获取用户购物车记录被勾选的商品的sku_id  set
            cart_selected_key = 'cart_selected_%s' % user.id
            # smembers(key): 获取redis中set的所有元素
            # (b'<sku_id>', b'<sku_id>', ...)
            redis_cart_selected = redis_conn.smembers(cart_selected_key) # Set

            # 组织数据
            # {
            #     '<sku_id>': {
            #         'count': '<count>',
            #         'selected': '<selected>'
            #     },
            #     ...
            # }
            cart_dict = {}

            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_cart_selected
                }
        else:
            # 2.2 如果用户未登录，从cookie中获取用户的购物车记录
            cookie_cart = request.COOKIES.get('cart') # None

            if cookie_cart:
                # 解析cookie购物车数据
                # {
                #     '<sku_id>': {
                #         'count': '<count>',
                #         'selected': '<selected>'
                #     },
                #     ...
                # }
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                cart_dict = {}

        # 3. 根据用户购物车中商品sku_id获取对应商品的信息
        sku_ids = cart_dict.keys()

        # select * from tb_sku where id in (1,2,3);
        skus = SKU.objects.filter(id__in=sku_ids)

        for sku in skus:
            # 给sku对象增加属性count和selected
            # 分别保存用户购物车中添加的该商品的数量和勾选状态
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        # 4. 将商品数据序列化并返回
        serializer = CartSKUSerializer(skus, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        购物车记录添加:
        1. 获取参数并进行校验(参数完整性，sku_id对应的商品是否存在，商品库存是否足够)
        2. 保存用户的购物车记录
            2.1 如果用户已登录，在redis中保存用户的购物车记录
            2.2 如果用户未登录，在cookie中保存用户的购物车记录
        3. 返回应答，购物车记录添加成功
        """
        # 1. 获取参数并进行校验(参数完整性，sku_id对应的商品是否存在，商品库存是否足够)
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取参数
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']

        # 获取user
        try:
            # 调用request.user会触发DRF的认证，在这里如果认证处理，可以自己进行处理
            user = request.user
        except Exception:
            user = None

        # 2. 保存用户的购物车记录
        if user is not None and user.is_authenticated:
            # 2.1 如果用户已登录，在redis中保存用户的购物车记录
            # 获取redis链接
            redis_conn = get_redis_connection('cart')

            # 在redis中存储用户的添加的商品的sku_id和对应数量count hash
            cart_key = 'cart_%s' % user.id

            pl = redis_conn.pipeline()
            # 如果sku_id商品在用户的购物车记录已经添加过，数量count需要进行累加
            # 如果sku_id商品在用户的购物车记录没有添加过，直接设置新的属性和值
            # hincrby(key, field, amount): 给hash指定的field的值累加amount，如果field不存在，新建属性和值
            pl.hincrby(cart_key, sku_id, count)

            # 在redis中存储用户购物车记录勾选状态 set
            cart_selected_key = 'cart_selected_%s' % user.id

            if selected:
                # 勾选
                # sadd(key, *members): 将set集合添加元素，不需要关注元素是否重复
                pl.sadd(cart_selected_key, sku_id)

            pl.execute()

            # 返回应答
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 2.2 如果用户未登录，在cookie中保存用户的购物车记录
            # 获取cookie中购物车数据
            cookie_cart = request.COOKIES.get('cart') # None

            if cookie_cart:
                # 解析购物车数据
                # {
                #     '<sku_id>': {
                #         'count': '<count>',
                #         'selected': '<selected>'
                #     },
                #     ...
                # }
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                cart_dict = {}

            # 保存购物车记录
            if sku_id in cart_dict:
                # 数量进行累加
                count += cart_dict[sku_id]['count']

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 3. 返回应答，购物车记录添加成功
            response = Response(serializer.data, status=status.HTTP_201_CREATED)

            # 设置购物车cookie数据
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode() # str
            response.set_cookie('cart', cart_data, max_age=constants.CART_COOKIE_EXPIRES)
            return response
