import redis
import pytest
import signal


class TimeOutEXception(Exception):
    pass

def setTimeOut(num,callback):
    def wrape(func):
        def handle(signum,frame):
            raise TimeOutEXception("超时")
        def toDo(*args,**kwargs):
            try:
                signal.signal(signal.SIGALRM,handle)
                signal.alarm(num)
                rs=func(*args,**kwargs)
                signal.alarm(0)
                return rs
            except TimeOutEXception as e:
                callback()
        return toDo
    return wrape




def timeout():
    print("超时未接收到数据")
    assert False


class Test_ineyes():
    def __init__(self):
        self.r=redis.Redis(host="139.198.4.56",port=6379)
    @setTimeOut(30,timeout)
    def sub(self,channel):
        """
        订阅结果的接收
        :return:
        """

        self.p=self.r.pubsub()
        self.p.subscribe(channel)
        for i in self.p.listen():
            if i['type']=='message':
                return True

t=Test_ineyes()


def test_test_channel():
    """
    测试种子测试结果
    :return:
    """

    assert t.sub("test_seeds")

def test_crawl_data():
    """
    测试正式发布结果
    :return:
    """

    assert t.sub("crawl_data")



if __name__=='__main__':
    print("开始测试...")
    pytest.main()