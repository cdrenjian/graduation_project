from py2neo import Graph,Node,Relationship



label='test_anet'   #操作基于anet类型的实体库



class Gra(object):
    def __init__(self):
        self.graph = Graph(
            "http://139.198.4.56:7474",
            username="neo4j",
            password="Tomato2017"
        )


    def create_node(self,property_dict):
        """根据属性创建节点"""
        node=Node(label,**property_dict)
        self.graph.create(node)
        return node



    def create_rel(self,node_1,node_2,rel_type='SELL'):
        """创建关系"""
        rel=Relationship(node_1,rel_type,node_2)
        self.graph.create(rel)
        return rel



if __name__=="__main__":
    g=Gra()
    print(g.create_node({'name':'菲纹-阿敏','company':'清涧县乐堂堡办事处工会联合会','birthday':'1990-09-27 00:00:00','lv':7,'city':'广东 东莞','follow':['蜜咖酱'],'url':'https://weibo.com/yangjunblogs?from=page_100505_profile&wvr=6&mod=bothfollow&refer_flag=1005050010_&is_all=1'}))

