from django.test import TestCase
import pickle
import base64
# Create your tests here.


# if __name__ == "__main__":
#     # base64编码之后的数据
#     req_data = 'gAN9cQAoSwF9cQEoWAgAAABzZWxlY3RlZHECiVgFAAAAY291bnRxA0sCdUsFfXEEKGgCiGgDSwF1dS4='
#
#     # # bas64解码
#     # res_data = base64.b64decode(req_data) # bytes
#     #
#     # # pickle.loads
#     # res_data = pickle.loads(res_data)
#
#     # 解析cookie购物车数据
#     res_data = pickle.loads(base64.b64decode(req_data))
#     print(res_data)


# if __name__ == "__main__":
#     # pickle.dumps(obj): 将obj转换为bytes字节流
#
#     # 假如未登录用户的购物车数据如下:
#     cart_dict = {
#         1: {
#             'count': 2,
#             'selected': False
#         },
#         5: {
#             'count': 1,
#             'selected': True
#         }
#     }
#
#     # res_data = pickle.dumps(cart_dict) # bytes
#     #
#     # # base64编码
#     # res_data = base64.b64encode(res_data) # bytes
#     #
#     # # bytes-> str
#     # res_data = res_data.decode()
#
#     # 设置购物车cookie数据
#     res_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
#
#     print(res_data)


# if __name__ == "__main__":
#     # picke.loads(bytes字节流): 将bytes字节流转换为obj
#     req_data = b'\x80\x03}q\x00(K\x01}q\x01(X\x08\x00\x00\x00selectedq' \
#                b'\x02\x89X\x05\x00\x00\x00countq\x03K\x02uK\x05}q\x04(h\x02\x88h\x03K\x01uu.'
#
#     res = pickle.loads(req_data)
#
#     print(res)


# if __name__ == "__main__":
#     # pickle.dumps(obj): 将obj转换为bytes字节流
#
#     # 假如未登录用户的购物车数据如下:
#     cart_dict = {
#         1: {
#             'count': 2,
#             'selected': False
#         },
#         5: {
#             'count': 1,
#             'selected': True
#         }
#     }
#
#     res_data = pickle.dumps(cart_dict)
#     print(res_data)
