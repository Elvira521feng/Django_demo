# 自定义分类页
from rest_framework.pagination import PageNumberPagination


class StandardResultPagination(PageNumberPagination):
    # 指定默认页容量
    page_size = 2
    # 指定获取分页数据时传递页容量参数名称
    page_size_query_param = 'page_size'
    # 指定最大页容量
    max_page_size = 20