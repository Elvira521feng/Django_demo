from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

# Create your models here.
from meiduo_mall.utils.models import BaseModel
from users import constants


class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    # openid = models.CharField(max_length=64, verbose_name='OpenID')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        """
        生成对应用户的邮箱验证的链接地址
        """
        # 组织用户数据
        data = {
            'id': self.id,
            'email': self.email
        }

        # 进行加密
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        token = serializer.dumps(data).decode() # str

        # 拼接验证的链接地址
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        """校验邮箱验证的token是否有效"""
        serializer = TJWSSerializer(settings.SECRET_KEY)

        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            # 获取用户id和email
            id = data.get('id')
            email = data.get('email')

            # 获取对应的用户
            user = User.objects.get(id=id, email=email)

            return user


# address
# address.province
# address.city
# address.district
class Address(BaseModel):
    """
    用户地址模型类
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
    # is_default = models.BooleanField(default=False, verbose_name='是否默认')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']


