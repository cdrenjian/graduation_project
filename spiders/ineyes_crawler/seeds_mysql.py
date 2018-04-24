import pymysql
import logging

logger=logging.getLogger()

class SeedsMysql(object):
    def __init__(self):
        self.db = pymysql.connect("139.198.4.56","tomato","Tomato2017","ineyes_seeds",charset="utf8")

    def select(self,status):
        with self.db.cursor() as cursor:
            sql = """SELECT * FROM seeds where status=%s"""%status
            try:
                cursor.execute(sql)
                self.db.commit()
            except Exception as e:
                raise e
            seeds = cursor.fetchall()  # 获得所有符合要求的种子
        return seeds

    def get_seeds(self,type=1):
        """
        获取所有的待爬种子
        """

        seeds = self.select(type)
        seeds_list = []
        page_rules=[]
        for seed in seeds:
            try:
                seed = list(seed)
                id = seed[0]
                name = seed[1]
                status = seed[2]
                fields = eval(seed[3])
                link_rules = list(eval(seed[4]))  #todo 允许link_rule和start_url为空，便于其他爬虫拓展
                if seed[5]:
                    page_rules = list(eval(seed[5]))   #todo 不使用eval来转换对象
                start_urls = list(eval(seed[6]))
                user_agent_type = seed[8]
                keywords = list(eval(seed[9])) if seed[9] else  None
                seed = [{"id":id,"name":name,"fields":fields,"link_rules":link_rules,"page_rules":page_rules,"status":status,"user_agent_type":user_agent_type,'keywords':keywords},start_urls]
            except Exception as e:
                logger.info("%s 种子解析错误: %s "%(id,e))
                seed = None
            if seed not in seeds_list and seed is not None:
                seeds_list.append(seed)
        return seeds_list

    def close(self):
        self.db.close()

