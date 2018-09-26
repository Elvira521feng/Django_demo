from django_redis import get_redis_connection
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from goods.models import SKU
from goods.serializers import SKUSerializer
from users import serializers, constants
from users.models import User


# POST /browse_histories/
from users.serializers import BrowseHistorySerializer


class BrowseHistoryView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BrowseHistorySerializer

    def get(self, request):
        """
        用户浏览记录获取:
        1. 从redis中获取登录用户浏览的商品sku_id
        2. 根据商品的id获取对应商品的数据
        3. 将商品的数据进行序列化并返回
        """
        # 获取登录user
        user = request.user

        # 1. 从redis中获取登录用户浏览的商品sku_id
        redis_conn = get_redis_connection('history')

        history_key = 'history_%s' % user.id

        # lrange(key, start, end): 获取redis列表指定区间内的元素
        # [b'<sku_id>', b'<sku_id>', ...]
        sku_ids = redis_conn.lrange(history_key, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)

        # 2. 根据商品的id获取对应商品的数据
        skus = []
        for sku_id in sku_ids:
            # 根据商品id获取商品信息
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)

        # 3. 将商品的数据进行序列化并返回
        serializer = SKUSerializer(skus, many=True)
        return Response(serializer.data)

    # def post(self, request):
    #     """
    #     request.user: 获取登录的用户
    #     用户浏览记录保存:
    #     1. 获取sku_id并进行校验(sku_id必传，sku_id对应的商品是否存在)
    #     2. 在redis中保存用户的浏览记录
    #     3. 返回应答，浏览记录保存成功
    #     """
    #     # 1. 获取sku_id并进行校验(sku_id必传，sku_id对应的商品是否存在)
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 2. 在redis中保存用户的浏览记录 (create)
    #     serializer.save()
    #
    #     # 3. 返回应答，浏览记录保存成功
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)



class VerifyEmailView(APIView):
    """
    邮箱验证
    """
    def put(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})


class EmailView(UpdateAPIView):
    """
    保存用户邮箱
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.EmailSerializer

    def get_object(self, *args, **kwargs):
        return self.request.user


class UserDetailView(RetrieveAPIView):
    """
    用户详情
    """
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


class UserView(CreateAPIView):
    """
        用户注册
        传入参数：
            username, password, password2, sms_code, mobile, allow
    """
    serializer_class = serializers.CreateUserSerializer


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = serializers.UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.filter(is_deleted=False).count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


