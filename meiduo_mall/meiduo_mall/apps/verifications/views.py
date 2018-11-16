import random

from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from celery_tasks.sms.tasks import send_sms_code
from meiduo_mall.libs.yuntongxun.sms import CCP
from verifications import constants
# Create your views here.

# 获取日志器
import logging
logger = logging.getLogger('django')


# GET /sms_codes/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(APIView):
    def get(self, request, mobile):
        """
        获取短信验证码:
        1. 给`mobile`手机号发送短信验证码
            1.1 随机生成一个6位数字
            1.2 在redis中保存短信验证码内容，以`mobile`为key，以短信验证码内容为value
            1.3 使用云通讯发送短信
        2. 返回应答，发送成功
        """
        redis_conn = get_redis_connection('verify_codes')
        # 判断60s之内是否给`mobilie`手机发送过短信
        send_flag = redis_conn.get('send_flag_%s' % mobile) # None

        if send_flag:
            return Response({'message': '发送短信过于频繁'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 给`mobile`手机号发送短信验证码
        # 1.1 随机生成一个6位数字
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info('短信验证码为: %s' % sms_code)

        # 1.2 在redis中保存短信验证码内容，以`mobile`为key，以短信验证码内容为value
        # 创建一个redis管道对象
        pl = redis_conn.pipeline()

        # 向redis管道中添加命令
        # redis_conn.set('<key>', '<value>', '<expires>')
        # redis_conn.setex('<key>', '<expires>', '<value>')
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 设置给`mobile`发送短信验证码标记
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 一次性执行管道中所有命令
        pl.execute()

        # 1.3 使用云通讯发送短信
        expires = constants.SMS_CODE_REDIS_EXPIRES // 60

        # try:
        #     res = CCP().send_template_sms(mobile, [sms_code, expires], constants.SMS_CODE_TEMP_ID)
        # except Exception as e:
        #     logger.error(e)
        #     return Response({'message': '发送短信异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        #
        # if res != 0:
        #     return Response({'message': '发送短信失败'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 2. 返回应答，发送成功
        # 发出发送短信的任务消息
        send_sms_code.delay(mobile, sms_code, expires)

        return Response({'message': 'OK'})
