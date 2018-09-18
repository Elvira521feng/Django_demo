import random

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.libs.yuntongxun.sms import CCP
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
        expires = constant.SMS_CODE_REDIS_EXPIRES

        # try:
        #     ccp = CCP()
        #     res = ccp.send_template_sms(mobile, [sms_code, expires], constant.SMS_CODE_TEMP_ID)
        # except Exception as e:
        #     logger.error(e)
        #     return Response({'message': '发送短信异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if res != 0:
            return Response({'message': '发送短信失败'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # send_sms_code.
        return Response({'message': 'OK'})







