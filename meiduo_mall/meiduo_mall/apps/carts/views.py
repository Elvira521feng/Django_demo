import base64
import pickle

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from carts import constants
from carts.serializers import CartSerializer


class CartView(APIView):
    """
    购物车
    """
    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入视图前就检查JWT
        """
        pass

    def post(self, request):
        """
        购物车记录添加
        """
        # 1. 获取参数(sku_id, count, selected)并进行参数校验
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']

        # 获取登录用户
        try:
            user = request.user
        except Exception as e:
            user = None

        if user and user.is_authenticated:
            # 2. 保存用户的购物车记录
            redis_conn = get_redis_connection('cart')
            pipeline = redis_conn.pipeline()
            cart_key = 'cart_%s' % user.id

            # 保存购物车中商品及数量
            pipeline.hincrby(cart_key, sku_id, count)

            # 保存购物车中商品的选中状态
            cart_selected_key = 'cart_selected_%s' % user.id
            if selected:
                pipeline.sadd(cart_selected_key, sku_id)

            pipeline.execute()

            # 3. 返回应答，保存购物车记录成功
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 获取客户端发送的cookie信息
            cookie_cart = request.COOKIES.get('cart')

            if cookie_cart:
                # 对cookie数据进行解析
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                count += cart_dict[sku_id]['count']

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 对cart_dict数据进行处理
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response.set_cookie('cart', cart_data, max_age=constants.CART_COOKIE_EXPIRES)
            return response
