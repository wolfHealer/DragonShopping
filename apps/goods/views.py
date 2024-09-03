from django.shortcuts import render

# Create your views here.
"""
关于模型的分析
1. 根据页面效果 尽量多的分析字段
2. 去分析是保存在一个表中 还是多个表中 （多举例说明）

分析表的关系的时候 最多不要超过3个表

多对多（一般是 3个表）

学生 和 老师

学生表
stu_id      stu_name

100             张三
200             李四

老师表
teacher_id  teacher_name
666             牛老师
999             齐老师


第三张表

stu_id      teacher_id
100             666
100             999
200             666
200             999

商品day01    模型的分析 --》  Fdfs(用于保存图片，视频等文件) --》 为了部署Fdfs学习Docker


"""

############上传图片的代码################################
# from fdfs_client.client import Fdfs_client
#
# # 1. 创建客户端
# # 修改加载配置文件的路径
# client=Fdfs_client('utils/fastdfs/client.conf')
#
# # 2. 上传图片
# # 图片的绝对路径
# client.upload_by_filename('/home/ubuntu/Desktop/img/c.png')

# 3. 获取file_id .upload_by_filename 上传成功会返回字典数据
# 字典数据中 有file_id
"""
{'Group name': 'group1', 'Remote file_id': 'group1/M00/00/02/wKgTgF-FCP-AHcq2AAMTeyk-Y3M402.png', 'Status': 'Upload successed.', 'Local file name': '/home/ubuntu/Desktop/img/c.png', 'Uploaded size': '196.00KB', 'Storage IP': '192.168.19.128'}

"""

from django.views import View
from utils.goods import get_categories
from apps.contents.models import ContentCategory

class IndexView(View):

    def get(self,request):

        """
        首页的数据分为2部分
        1部分是 商品分类数据
        2部分是 广告数据

        """
        # 1.商品分类数据
        categories=get_categories()
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
        # 模板使用比较少，以后大家到公司 自然就会了
        return render(request,'index.html',context)

"""
需求：
        根据点击的分类，来获取分类数据（有排序，有分页）
前端：
        前端会发送一个axios请求， 分类id 在路由中， 
        分页的页码（第几页数据），每页多少条数据，排序也会传递过来
后端：
    请求          接收参数
    业务逻辑       根据需求查询数据，将对象数据转换为字典数据
    响应          JSON

    路由      GET     /list/category_id/skus/
    步骤
        1.接收参数
        2.获取分类id
        3.根据分类id进行分类数据的查询验证
        4.获取面包屑数据
        5.查询分类对应的sku数据，然后排序，然后分页
        6.返回响应
"""
from apps.goods.models import GoodsCategory
from django.http import JsonResponse
from utils.goods import get_breadcrumb
from apps.goods.models import SKU
class ListView(View):

    def get(self,request,category_id):
        # 1.接收参数
        # 排序字段
        ordering=request.GET.get('ordering')
        # 每页多少条数据
        page_size=request.GET.get('page_size')
        # 要第几页数据
        page=request.GET.get('page')

        # 2.获取分类id
        # 3.根据分类id进行分类数据的查询验证
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        # 4.获取面包屑数据
        breadcrumb=get_breadcrumb(category)

        # 5.查询分类对应的sku数据，然后排序，然后分页
        skus=SKU.objects.filter(category=category,is_launched=True).order_by(ordering)
        # 分页
        from django.core.paginator import Paginator
        # object_list, per_page
        # object_list   列表数据
        # per_page      每页多少条数据
        paginator=Paginator(skus,per_page=page_size)

        #获取指定页码的数据
        page_skus=paginator.page(page)

        sku_list=[]
        #将对象转换为字典数据
        for sku in page_skus.object_list:
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url
            })

        # 获取总页码
        total_num = paginator.num_pages

        # 6.返回响应
        return JsonResponse({'code':0,'errmsg':'ok','list':sku_list,'count':total_num,'breadcrumb':breadcrumb})


########################################################################
"""
搜索 

1. 我们不使用like

2. 我们使用 全文检索
    全文检索即在指定的任意字段中进行检索查询
    
3. 全文检索方案需要配合搜索引擎来实现

4. 搜索引擎
    
    原理：  关键词与词条的对应关系，并记录词条的位置
                                            
    
        1  --- 我爱北京天安门                      我爱， 北京，天安门
        
        2 --- 王红，我爱你，我想你想的睡不着觉        王红，我爱，我爱你，睡不着觉，想你，
        
        3 ---  我睡不着觉                          我，睡不着觉 
        
        
        我爱


5. Elasticsearch
    进行分词操作 
    分词是指将一句话拆解成多个单字或词，这些字或词便是这句话的关键词
    
    下雨天 留客天 天留我不 留
    
    
6. 
    数据         <----------Haystack--------->             elasticsearch 
                        
                        ORM(面向对象操作模型)                 mysql,oracle,sqlite,sql server
"""

"""
 我们/数据         <----------Haystack--------->             elasticsearch 

 我们是借助于 haystack 来对接 elasticsearch
 所以 haystack 可以帮助我们 查询数据
"""
from haystack.views import SearchView
from django.http import JsonResponse


class SKUSearchView(SearchView):

    def create_response(self):
        # 获取搜索的结果
        context = self.get_context()
        # 我们该如何知道里边有什么数据呢？？？
        # 添加断点来分析
        sku_list=[]
        for sku in context['page'].object_list:
            sku_list.append({
                'id':sku.object.id,
                'name':sku.object.name,
                'price': sku.object.price,
                'default_image_url': sku.object.default_image.url,
                'searchkey': context.get('query'),
                'page_size': context['page'].paginator.num_pages,
                'count': context['page'].paginator.count
            })

        return JsonResponse(sku_list,safe=False)


"""
需求：
    详情页面
    
    1.分类数据
    2.面包屑
    3.SKU信息
    4.规格信息
    
    
    我们的详情页面也是需要静态化实现的。
    但是我们再讲解静态化之前，应该可以先把 详情页面的数据展示出来

"""
from utils.goods import get_categories
from utils.goods import get_breadcrumb
from utils.goods import get_goods_specs
class DetailView(View):

    def get(self,request,sku_id):
        try:
            sku=SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            pass
        # 1.分类数据
        categories=get_categories()
        # 2.面包屑
        breadcrumb=get_breadcrumb(sku.category)
        # 3.SKU信息
        # 4.规格信息
        goods_specs=get_goods_specs(sku)

        context = {

            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,

        }
        return render(request,'detail.html',context)



"""
需求：
    统计每一天的分类商品访问量

前端：
    当访问具体页面的时候，会发送一个axios请求。携带分类id
后端：
    请求：         接收请求，获取参数
    业务逻辑：       查询有没有，有的话更新数据，没有新建数据
    响应：         返回JSON
    
    路由：     POST    detail/visit/<category_id>/
    步骤：
        
        1.接收分类id
        2.验证参数（验证分类id）
        3.查询当天 这个分类的记录有没有
        4. 没有新建数据
        5. 有的话更新数据
        6. 返回响应
    

"""
from apps.goods.models import GoodsVisitCount
from datetime import date
class CategoryVisitCountView(View):

    def post(self,request,category_id):
        # 1.接收分类id
        # 2.验证参数（验证分类id）
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此分类'})
        # 3.查询当天 这个分类的记录有没有

        today=date.today()
        try:
            gvc=GoodsVisitCount.objects.get(category=category,date=today)
        except GoodsVisitCount.DoesNotExist:
            # 4. 没有新建数据
            GoodsVisitCount.objects.create(category=category,
                                           date=today,
                                           count=1)
        else:
            # 5. 有的话更新数据
            gvc.count+=1
            gvc.save()
        # 6. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})

