"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import datetime
import os
import sys
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将`apps`目录添加到`sys.path`搜索路径中
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# print(sys.path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7s09%_!e5fm!wxw3&d%%v+#+qzu0(l%oowtfz#!pvbv8l&p!2d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['api.meiduo.site', '127.0.0.1', 'localhost', 'www.meiduo.site']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'ckeditor',  # 富文本编辑器
    'ckeditor_uploader',  # 富文本编辑器上传图片模块
    'django_crontab',  # 定时任务
    'haystack', # 全文检索框架
    'xadmin',
    'crispy_forms',
    'reversion',
    'pics.apps.PicsConfig',
    # 'meiduo_mall.apps.users.apps.UsersConfig',
    'users.apps.UsersConfig',
    'verifications.apps.VerificationsConfig',
    'oauth.apps.OauthConfig',
    'areas.apps.AreasConfig',
    'contents.apps.ContentsConfig',
    'goods.apps.GoodsConfig',
    'cart.apps.CartConfig',
    'orders.apps.OrdersConfig',
    'payment.apps.PaymentConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 指定模板文件的目录
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '172.16.179.139',
        'PORT': 3306,
        'USER': 'meiduo_sh16',
        'PASSWORD': 'meiduo',
        'NAME': 'meiduo_mall_sh16',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# Django缓存设置(默认Django的缓存就是服务器内存)
# 这里是把Django的缓存设置为redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 指定缓存空间对应的redis地址
        "LOCATION": "redis://172.16.179.139:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://172.16.179.139:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    # 保存短信验证码内容
    "verify_codes": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 指定缓存空间对应的redis地址
        "LOCATION": "redis://172.16.179.139:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    # 保存浏览记录
    "history": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 指定缓存空间对应的redis地址
        "LOCATION": "redis://172.16.179.139:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    # 保存购物车记录
    "cart": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 指定缓存空间对应的redis地址
        "LOCATION": "redis://172.16.179.139:6379/5",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}

# 设置将Django的session存储到缓存中(缓存已经变成了redis，所以session会存储到redis中)
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# 指定session信息存储到缓存空间名称
SESSION_CACHE_ALIAS = "session"

# 获取redis链接
# from redis import StrictRedis
# redis_conn = StrictRedis(host='172.16.179.139', port=6379, db=2)

# 通过django-redis获取redis链接
# from django_redis import get_redis_connection
# redis_conn = get_redis_connection('verify_codes') # 返回就是StrictRedis类对象


# Django日志存储设置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/meiduo.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

# 打印日志
# 获取日志器
# import logging
# logger = logging.getLogger('django')
# logger.error('ERROR Message')
# logger.info('INFO Message')


REST_FRAMEWORK = {
    # 异常处理
    'EXCEPTION_HANDLER': 'meiduo_mall.utils.exceptions.exception_handler',
    # 认证机制
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 添加JWT认证机制 401: 未认证
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    # 分页
    'DEFAULT_PAGINATION_CLASS': 'meiduo_mall.utils.pagination.StandardResultPagination',
}

# JWT扩展设置
JWT_AUTH = {
    # 设置生成jwt token数据时，token数据的有效时间
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 指定JWT扩展登录视图获取响应数据方法
    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'users.utils.jwt_response_payload_handler',
}

# 指定Django认证系统所使用的用户模型类
# AUTH_USER_MODEL = '应用名.模型类'
AUTH_USER_MODEL = 'users.User'


# CORS跨域请求的设置
# 白名单
CORS_ORIGIN_WHITELIST = (
    '127.0.0.1:8080',
    'localhost:8080',
    'www.meiduo.site:8080',
    'www.meiduo.site',
)

CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie


# 指定Django认证的后端类
AUTHENTICATION_BACKENDS = [
    'users.utils.UsernameMobileAuthBackend',
]

# QQ登录开发设置
QQ_CLIENT_ID = '101474184' # QQ开发应用APPID
QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c' # QQ开发应用APP-KEY
QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html' # 网站回调地址
QQ_STATE = '/' # QQ登录成功之后跳转页面地址


# 邮件发送设置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# SMTP服务器地址
EMAIL_HOST = 'smtp.163.com'
# SMTP服务端口号
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = 'smartli_it@163.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'smart123lz'
# 收件人看到的发件人
EMAIL_FROM = '美多商城<smartli_it@163.com>'


# DRF扩展
REST_FRAMEWORK_EXTENSIONS = {
    # 缓存时间
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,
    # 缓存存储
    'DEFAULT_USE_CACHE': 'default',
}


# FDFS配置
FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')
FDFS_URL = 'http://image.meiduo.site:8888/'


# 指定Django使用文件存储类
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.fdfs_storage.FDFSStorage'


# 富文本编辑器ckeditor配置
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # 工具条功能
        'height': 300,  # 编辑器高度
        # 'width': 300,  # 编辑器宽
    },
}
CKEDITOR_UPLOAD_PATH = ''  # 上传图片保存路径，使用了FastDFS，所以此处设为''


# 指定生成静态文件页面保存目录
GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc')

# 定时任务设置
CRONJOBS = [
    # 每1分钟执行一次生成主页静态文件
    ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> ' + os.path.dirname(BASE_DIR) + '/logs/crontab.log')
]

# 解决crontab中文问题
CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'


# Haystack全文检索框架设置
HAYSTACK_CONNECTIONS = {
    'default': {
        # 指定haystack全文检索框架使用搜索引擎
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        # 此处为elasticsearch运行的服务器ip地址，端口号固定为9200
        'URL': 'http://172.16.179.139:9200/',
        # 指定elasticsearch建立的索引库的名称
        'INDEX_NAME': 'meiduo_sh16',
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'


# 支付宝
ALIPAY_APPID = "2016090800464054" # 开发应用APPID
ALIPAY_URL = "https://openapi.alipaydev.com/gateway.do" # 支付宝网关地址
ALIPAY_DEBUG = True # 使用沙箱环境

# 指定收集静态文件的保存目录
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc/static')

