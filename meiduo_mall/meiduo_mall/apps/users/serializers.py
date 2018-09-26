import re

from django.conf import settings
from django.core.mail import send_mail
from django_redis import get_redis_connection
from rest_framework import serializers

from celery_tasks.email.tasks import send_verify_email
from goods.models import SKU
from users import constants
from users.models import User, Address


class BrowseHistorySerializer(serializers.Serializer):
    """浏览记录添加的序列化器类"""
    sku_id = serializers.IntegerField(label='商品sku编号')

    def validate_sku_id(self, value):
        """sku_id对应的商品是否存在"""
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return value

    def create(self, validated_data):
        """在redis中保存用户的浏览记录"""
        # 获取商品sku_id
        sku_id = validated_data['sku_id']

        # 获取redis链接
        redis_conn = get_redis_connection('history')

        # 获取登录user
        user = self.context['request'].user

        # 拼接key
        history_key = 'history_%s' % user.id

        # 去重: 如果用户已经浏览过某个商品，先将商品sku_id从redis列表元素中移除
        # lrem(key, count, value): 从redis列表中移除元素，如果元素不存在，直接忽略
        redis_conn.lrem(history_key, 0, sku_id)

        # 左侧加入: 将用户最新浏览的商品id从左侧加入redis列表元素，保持浏览顺序
        # lpush(key, *values): 从redis列表的左侧加入元素
        redis_conn.lpush(history_key, sku_id)

        # 列表截取: 只保留用户最新浏览的几个商品sku_id
        # ltrim(key, start, stop): 保留redis列表指定区间内的元素
        redis_conn.ltrim(history_key, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)

        return validated_data


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)


class EmailSerializer(serializers.ModelSerializer):
    """用户邮箱设置序列化器类"""
    class Meta:
        model = User
        fields = ('id', 'email')

    def update(self, instance, validated_data):
        """
        设置user用户的邮箱并发送邮箱验证邮件
        instance: 创建序列化器时传递对象
        validated_data: 验证之后的数据
        """
        # 设置用户的邮箱
        email = validated_data['email']
        instance.email = email
        instance.save()

        # TODO: 发送邮箱的验证邮件
        # 生成邮箱验证的链接地址: http://www.meiduo.site:8080/success_verify_email.html?user_id=<user_id>
        # 如果链接地址中直接存储用户的信息，可能会造成别人的恶意请求
        # 在生成箱验证的链接地址时，对用户的信息进行加密生成token，把加密之后token放在链接地址中
        # http://www.meiduo.site:8080/success_verify_email.html?token=<token>
        verify_url = instance.generate_verify_email_url()

        # 发出发送邮件的任务消息
        send_verify_email.delay(email, verify_url)

        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """用户个人信息序列化器类"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class CreateUserSerializer(serializers.ModelSerializer):
    """
    创建用户的序列化器类
    """
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='是否同意协议', write_only=True)
    token = serializers.CharField(label='JWT Token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'mobile', 'password2', 'sms_code', 'allow', 'token')

        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_allow(self, value):
        """是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意协议')

        return value

    def validate_mobile(self, value):
        """手机号格式，手机号是否已经注册"""
        # 手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')

        # 手机号是否已经注册
        count = User.objects.filter(mobile=value).count()

        if count > 0:
            raise serializers.ValidationError('手机号已注册')

        return value

    def validate(self, attrs):
        """两次密码是否一致，短信验证码是否正确"""
        # 两次密码是否一致
        password = attrs['password']
        password2 = attrs['password2']

        if password != password2:
            raise serializers.ValidationError('两次密码不一致')

        # 获取手机号
        mobile = attrs['mobile']

        # 从redis中获取真实的短信验证码内容
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile) # bytes

        if not real_sms_code:
            raise serializers.ValidationError('短信验证码已过期')

        # 对比短信验证码
        sms_code = attrs['sms_code'] # str

        # bytes->str
        real_sms_code = real_sms_code.decode()
        if real_sms_code != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        return attrs

    def create(self, validated_data):
        """保存注册用户的信息"""
        # 清除无用的数据
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 保存注册用户的信息
        user = User.objects.create_user(**validated_data)

        # 由服务器生成一个jwt token数据，包含登录用户身份信息
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 生成载荷
        payload = jwt_payload_handler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)

        # 给user对象增加属性token，保存服务器签发jwt token数据
        user.token = token

        # 返回注册用户
        return user









