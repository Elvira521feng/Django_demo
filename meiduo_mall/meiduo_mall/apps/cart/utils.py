# 封装购物车合并方法
import base64
import pickle

from django_redis import get_redis_connection


def merge_cookie_cart_to_redis(request, user, response):
    """合并cookie购物车数据到redis数据库中"""
    # 获取cookie中的购物车数据
    cookie_cart = request.COOKIES.get('cart') # None

    if cookie_cart is None:
        return

    # 解析cookie中的购物车数据
    # {
    #     '<sku_id>': {
    #         'count': '<count>',
    #         'selected': '<selected>',
    #     },
    #     ...
    # }
    cart_dict = pickle.loads(base64.b64decode(cookie_cart)) # {}

    if not cart_dict:
        # 字典数据为空
        return

    # 组织数据

    # 保存cookie购物车数据中对应商品的sku_id和数量count，此字典中的数据在进行合并时需要添加到redis中对应hash中
    # {
    #     '<sku_id>': '<count>',
    #     ...
    # }
    cart = {}

    # 保存cookie购物车数据中被勾选的商品的sku_id，合并时需要将此列表中数据添加到redis中对应set中
    redis_cart_add = []

    # 保存cookie购物车数据中未被勾选的商品的sku_id，合并时需要将此列表中的数据从redis中对应set中移除
    redis_cart_remove = []

    for sku_id, count_selected in cart_dict.items():
        cart[sku_id] = count_selected['count']

        if count_selected['selected']:
            # 勾选
            redis_cart_add.append(sku_id)
        else:
            # 未勾选
            redis_cart_remove.append(sku_id)

    # 进行购物车记录合并
    redis_conn = get_redis_connection('cart')

    # 向redis中合并cookie中购物车中添加的商品的sku_id和数量count   hash
    cart_key = 'cart_%s' % user.id
    # hmset key field value [field value ...]
    # hmset(key, dict): 将dict字典中key和value作为属性和值设置到hash中，如果属性已存在，会将值进行覆盖，否则创建新的属性和值
    redis_conn.hmset(cart_key, cart)

    # 向redis中合并cookie中购物车记录勾选状态  set
    cart_selected_key = 'cart_selected_%s' % user.id

    if redis_cart_add:
        redis_conn.sadd(cart_selected_key, *redis_cart_add)

    if redis_cart_remove:
        redis_conn.srem(cart_selected_key, *redis_cart_remove)

    # 删除cookie中的购物车
    response.delete_cookie('cart')

















