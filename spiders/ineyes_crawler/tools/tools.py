import socket
import xdrlib, sys
import xlrd
import requests
import re

def get_host_ip():
    """
    获取本地ip
    :return:
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip



def get_proxy():
    """从代理池获取ip"""
    ip=requests.get('http://139.198.4.56:8900/get').text
    print('当前代理ip{}'.format(ip))
    service_args=[
    '--proxy={}'.format(ip),
    '--proxy-type=https',
    ]
    return service_args



def count_filter(count):
    # 处理评论数的编码，提取评论
    count=str(count)
    if "亿" in count:
        x = 100000000
    elif "万" in count:
        x = 10000
    else:
        x = 1
    count = "".join([s for s in count if s.isdigit() or s == '.'])  # 提取数字
    if not count:
        return 0
    count = float(count) * x
    return int(count)



def keywords_from_excel(filename):
    """读取关键词excel文件"""
    data = xlrd.open_workbook(filename)
    table = data.sheet_by_index(0)
    colnames=table.row_values(0) if '关键字' in table.row_values(0) else table.row_values(1)  #，考虑表名的存在，开头两行里取字段名。
    try:
        kw_index=colnames.index('关键字')  #获得关键词索引
    except Exception as e:
        print(e)
        raise e
    kw_values=[i for i in table.col_values(kw_index)  if i.strip()] #获取关键词竖列的的数据并清洗空值
    start_num=kw_values.index('关键字')+1
    kw_values=set(kw_values[start_num:])
    return kw_values



def find_toutiao_avatar_url(url):
    """头条作者主页头像使用伪元素无法直接用xpath定位元素，故采取正则提取"""
    rule=r'avatar_url":"(http.*?)"'
    headers={"user-agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)"}
    html = requests.get(url,headers=headers).content
    print(str(html))
    pattern = re.compile(rule, re.I | re.M)
    urls = pattern.findall(str(html))
    return urls[0]



if __name__=='__main__':
    find_toutiao_avatar_url('https://www.toutiao.com/c/user/6727102876/#mid=6727102876')








