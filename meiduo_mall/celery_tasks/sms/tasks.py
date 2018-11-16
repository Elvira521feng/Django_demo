# 封装任务函数
from celery_tasks.main import celery_app
from celery_tasks.sms.yuntongxun.sms import CCP

# 发送短信模板ID
SMS_CODE_TEMP_ID = 1

# 获取logger
import logging
logger = logging.getLogger('django')


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code, expires):
    print('发送短信的任务函数被调用')

    try:
        res = CCP().send_template_sms(mobile, [sms_code, expires], SMS_CODE_TEMP_ID)
    except Exception as e:
        logger.error('发送短信异常：[mobile: %s]-[sms_code: %s]' % (mobile, sms_code))
    else:
        if res != 0:
            logger.error('发送短信失败：[mobile: %s]-[sms_code: %s]' % (mobile, sms_code))
        else:
            logger.info('发送短信成功：[mobile: %s]-[sms_code: %s]' % (mobile, sms_code))

