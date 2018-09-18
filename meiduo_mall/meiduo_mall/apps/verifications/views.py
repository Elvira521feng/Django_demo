import random

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from celery_tasks.sms.tasks import send_sms_code
from verifications import constant

import logging
logger = logging.getLogger('django')


class SMSCodesView(APIView):
    """
    短信验证码
    传入参数：
        mobile
    """
    def get(self, request, mobile):
        """发送验证码"""
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get('send_flag_%s' % mobile)

        if send_flag:
            return Response({'message': '发送短信过于频繁'}, status=status.HTTP_400_BAD_REQUEST)

        sms_code = '%06d' % random.randint(0, 999999)
        logger.info('短信验证码为: %s' % sms_code)

        pl = redis_conn.pipeline()

        # 保存短信验码与发送记录
        pl.setex('sms_%s' % mobile, constant.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constant.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        res = 0

        # 发送短信验证码
        sms_code_expires = constant.SMS_CODE_REDIS_EXPIRES // 60
        send_sms_code.delay(mobile, sms_code, sms_code_expires)

        return Response({'message': 'OK'})







