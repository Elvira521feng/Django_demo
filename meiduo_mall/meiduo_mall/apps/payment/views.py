import os

from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from orders.models import OrderInfo
from payment.models import Payment
from alipay import AliPay

# Create your views here.

# charset=utf-8&
# out_trade_no=201809300856190000000002& # 商户订单id
# method=alipay.trade.page.pay.return&
# total_amount=3398.00&
# 签名字符串
# sign=qCtnsUNnDOqn2XrbEpXtbZ9Aa5YzsM%2BcUyXYSZFmzzKhMB%2FTsHYcv%2F%2BBGa7CV7UXiFHlpwhYkzyWhOGXYl7f5KZy2DMEH8tyhct7107rIee%2FB19o6wTZD%2FYoQUt8K9EdsXLoBxID3inO8fAdc43Y9Xh8S2Lh%2BasuNdAUeGXYDQgL8fNGjBYy5VJ3bX2dgFUyruuVqwvNe2XTqYlymIxkGkR0TieZWDkif0SWeQemmUHgYDcs3QAunmu7OrFVqTcN8heEt6Y7tXDsB6%2FU%2FoqGO4KqBkmEh8YQwbPxMlcfSRx7aWoy3qNTtworZcRjo6pmKHv6CVskABQU64G5V7BJsQ%3D%3D&
# trade_no=2018093021001004920500444104& # 支付宝交易号
# auth_app_id=2016090800464054&
# version=1.0&
# app_id=2016090800464054&
# sign_type=RSA2&
# seller_id=2088102174694091&
# timestamp=2018-09-30+08%3A56%3A56


# PUT /payment/status/?支付结果参数
class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """
        保存支付结果:
        1. 获取参数并进行签名验证
        2. 订单是否有效
        3. 保存支付结果
        4. 返回应答
        """
        # 1. 获取参数并进行签名验证
        data = request.query_params.dict()
        signature = data.pop('sign')

        # 初始化
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,  # 开发应用APPID
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False，是否使用沙箱环境
        )

        success = alipay.verify(data, signature)

        if not success:
            # 签名验证失败
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)

        # 2. 订单是否有效
        order_id = data.get('out_trade_no')
        try:
            order = OrderInfo.objects.get(
                order_id=order_id,
                user=request.user,
                pay_method=OrderInfo.PAY_METHODS_ENUM['ALIPAY'],  # 支付宝支付
                status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']  # 待支付
            )
        except OrderInfo.DoesNotExist:
            return Response({'message': '无效的订单信息'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. 保存支付结果
        trade_id = data.get('trade_no')
        Payment.objects.create(
            order=order,
            trade_id=trade_id
        )

        # 修改订单状态
        order.status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        order.save()

        # 4. 返回应答
        return Response({'trade_id': trade_id})


# GET /orders/(?P<order_id>\d+)/payment/
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        """
        获取支付宝支付网址和参数:
        1. 获取参数并进行校验(订单是否有效)
        2. 组织支付宝支付网址和参数
        3. 返回支付宝支付网址
        """
        # 获取登录user
        user = request.user
        # 1. 获取参数并进行校验(订单是否有效)
        try:
            order = OrderInfo.objects.get(
                order_id=order_id,
                user=user,
                pay_method=OrderInfo.PAY_METHODS_ENUM['ALIPAY'], # 支付宝支付
                status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] # 待支付
            )
        except OrderInfo.DoesNotExist:
            return Response({'message': '无效的订单信息'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. 组织支付宝支付网址和参数
        # 初始化
        alipay = AliPay(
            appid=settings.ALIPAY_APPID, # 开发应用APPID
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False，是否使用沙箱环境
        )

        # 组织支付参数
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id, # 订单编号
            total_amount=str(order.total_amount), # 订单总金额
            subject='美多商城%s' % order_id, # 订单标题
            return_url='http://www.meiduo.site:8080/pay_success.html', # 回调地址
            notify_url=None  # 可选, 不填则使用默认notify url
        )

        # 3. 返回支付宝支付网址
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return Response({'alipay_url': alipay_url})
