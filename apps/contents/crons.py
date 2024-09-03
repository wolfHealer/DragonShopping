#######################################################################
"""
首页，详情页面

我们都是先查询数据库的数据
然后再进行HTML页面的渲染

不管是 数据库的数据缓存 还是 HTML页面的渲染（特别是分类渲染，比较慢） 多少都会影响用户的体验

最好的体验 是
用户  直接 就可以访问到  经过数据库查询，已经渲染的HTML页面 静态化


 经过数据库查询，已经渲染的HTML页面，写入到指定目录

"""
# 这个函数 能够帮助我们 数据库查询，渲染HTML页面，然后把渲染的HTML写入到指定文件
import time
from utils.goods import get_categories
from apps.contents.models import ContentCategory

def generic_meiduo_index():
    print('--------------%s-------------'%time.ctime())
    # 1.商品分类数据
    categories = get_categories()
    # 2.广告数据
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 我们的首页 后边会讲解页面静态化
    # 我们把数据 传递 给 模板
    context = {
        'categories': categories,
        'contents': contents,
    }

    # 1. 加载渲染的模板
    from django.template import loader
    index_template=loader.get_template('index.html')

    # 2. 把数据给模板
    index_html_data=index_template.render(context)
    # 3. 把渲染好的HTML，写入到指定文件
    from DragonShopping import settings
    import os
    # base_dir 的上一级
    file_path=os.path.join(os.path.dirname(settings.BASE_DIR),'front_end_pc/index.html')

    with open(file_path,'w',encoding='utf-8') as f:
        f.write(index_html_data)



