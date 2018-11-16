from celery import Celery

# 设置Django运行所依赖的环境变量
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 创建Celery类的对象
celery_app = Celery('celery_tasks')

# 加载配置
celery_app.config_from_object('celery_tasks.config')

# 启动worker时自动发现任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.html'])