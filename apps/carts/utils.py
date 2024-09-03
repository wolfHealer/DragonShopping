"""
需求：
        登录的时候，将cookie数据合并到redis中
前端：

后端：
    请求：         在登录的时候，获取cookie数据
    业务逻辑：       合并到redis中
    响应：

抽象的问题 具体化（举个例子）

1. 读取cookie数据
2. 初始化一个字典 用于保存 sku_id:count
    初始化一个列表 用于保存选中的商品id
    初始化一个列表 用于保存未选中的商品id
3. 遍历cookie数据
4. 将字典数据，列表数据分别添加到redis中
5. 删除cookie数据

#######################################

redis       hash
                    1:10
                    3:10
            set
                    1

cookie
        {
            1: {count:666,selected:True},
            2: {count:999,selected:True},
            5: {count:999,selected:False},
        }

hash
1:666       1
2:999       1

 ① 当cookie数据和redis数据 有相同的商品id的时候，数量怎么办？？？ 我们以cookie为主
 ② 当cookie数据有，redis数据没有的， 全部以 cookie为主
 ③ 当redis中有的数据，cookie没有。  不动



"""
import pickle
import base64

from django_redis import get_redis_connection


def merge_cookie_to_redis(request,response):
    """
    抽象的问题 具体化（举个例子）

        1. 读取cookie数据
        2. 初始化一个字典 用于保存 sku_id:count
            初始化一个列表 用于保存选中的商品id
            初始化一个列表 用于保存未选中的商品id
        3. 遍历cookie数据
        4. 将字典数据，列表数据分别添加到redis中
        5. 删除cookie数据
    :return:
    """
    # 1. 读取cookie数据
    cookie_carts = request.COOKIES.get('carts')

    if cookie_carts is not None:
        carts=pickle.loads(base64.b64decode(cookie_carts))

        # 2. 初始化一个字典 用于保存 sku_id:count
        # {sku_id:count,sku_id:count,....}
        cookie_dict={}
        #     初始化一个列表 用于保存选中的商品id
        selected_ids=[]
        #     初始化一个列表 用于保存未选中的商品id
        unselected_ids=[]

        # 3. 遍历cookie数据
        """
        {
            1: {count:666,selected:True},
            2: {count:999,selected:True},
            5: {count:999,selected:False},
        }
        """
        for sku_id,count_selected_dict in carts.items():
            # 1: {count:666,selected:True},
            # 字典数据
            cookie_dict[sku_id]=count_selected_dict['count']
            if count_selected_dict['selected']:
                selected_ids.append(sku_id)
            else:
                unselected_ids.append(sku_id)
        user=request.user
        # 4. 将字典数据，列表数据分别添加到redis中
        redis_cli=get_redis_connection('carts')
        pipeline=redis_cli.pipeline()
        #  {sku_id:count,sku_id:count,....}
        pipeline.hmset('carts_%s'%user.id,cookie_dict)
        # selected_id [1,3,2]
        if len(selected_ids)>0:
            # *selected_ids  对列表数据进行解包
            pipeline.sadd('selected_%s'%user.id,*selected_ids)
        # unselected_id [4,5,6]
        if len(unselected_ids)>0:
            pipeline.srem('selected_%s'%user.id,*unselected_ids)

        pipeline.execute()

        # 5. 删除cookie数据
        response.delete_cookie('carts')

    # response 最好返回
    return response