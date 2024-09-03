#!/usr/bin/env python

# ../ 当前目录的上一级目录，也就是 base_dir
import sys
sys.path.insert(0, '../')

# 告诉 os 我们的django的配置文件在哪里
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DragonShopping.settings")

# django setup
# 相当于 当前的文件 有了django的环境
import django
django.setup()


from utils.goods import get_categories,get_goods_specs,get_breadcrumb
from apps.goods.models import SKU

def generic_detail_html(sku):
    # try:
    #     sku = SKU.objects.get(id=sku_id)
    # except SKU.DoesNotExist:
    #     pass
    # 1.分类数据
    categories = get_categories()
    # 2.面包屑
    breadcrumb = get_breadcrumb(sku.category)
    # 3.SKU信息
    # 4.规格信息
    goods_specs = get_goods_specs(sku)

    context = {

        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs,

    }

    # 1. 加载模板
    from django.template import loader
    detail_template=loader.get_template('detail.html')
    # 2. 模板渲染
    detail_html_data=detail_template.render(context)
    # 3. 写入到指定文件
    import os
    from DragonShopping import settings
    file_path=os.path.join(os.path.dirname(settings.BASE_DIR),'front_end_pc/goods/%s.html'%sku.id)

    with open(file_path,'w',encoding='utf-8') as f:
        f.write(detail_html_data)

    print(sku.id)


skus=SKU.objects.all()
for sku in skus:
    generic_detail_html(sku)

"""
详情页面 与 首页不同
详情页面的内容变化比较少。一般也就是修改商品的价格

1. 详情页面 应该在上线的时候 统一都生成一遍
2. 应该是运营人员修改的时候生成 （定时任务）

"""