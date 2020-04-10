#导入所需包
import urllib.request,requests
from lxml import etree
import time
import re  #正则表达式
import json
from bs4 import BeautifulSoup
import pymysql

def jd_spider(url,startPage,endPage):
    #对页码进行编辑
    for page in range(startPage,endPage + 1):
        #奇数递增
        pn = page*2 - 1
        print("正在抓取第{}页".format(page))
        #拼接url  1、3、5、7
        full_url = url +"&page="+str(pn)
        #print(full_url)
        #读取网站源代码
        loadPage(full_url)
        time.sleep(1)#休息1秒

def loadPage(url):
    #定义请求头
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }
    #定义请求 urllib.request.Request()
    request = urllib.request.Request(url,headers=headers)
    # 发送请求获取响应数据,第一次爬取拿到所有商品的详情页面url
    html = urllib.request.urlopen(request).read()
    content = etree.HTML(html)
    urls = content.xpath('//div[@class="gl-i-wrap"]/div[@class="p-img"]/a/@href')

    #清洗url（将url中的https:  截取掉）
    for u in range(1,31):
        try:
            #截取 :之前的数据，生成新的url
            result = re.split(r":",urls[u-1])[1]
            urls[u-1] = result
        except Exception as e:
            continue
    #获取详情页面的url
    for u in urls:
        new_url = "https:"+ u
        #二次爬取详情页面中的商品数据
        request = urllib.request.Request(new_url, headers=headers)
        html = urllib.request.urlopen(request).read()
        # 对详情页面解析，使用xpath获取商品详细数据
        content = etree.HTML(html)
        # 获取商品标题品牌
        brand = content.xpath('.//div[@class="product-intro clearfix"]/div[@class="itemInfo-wrap"]/div[@class="sku-name"]/text()')
        try:
            if len(brand) == 1:
                name = brand[0]
            else:
                name = brand[1]
        except Exception as e:
            continue
        name = str(name)
        list_name = name.strip()
        # print(type(name))
        # print(list_name)

        # 获取商品ID
        # print(type(new_url))
        sku_id = re.findall('\d+',new_url)
        # print(sku_id[0])

        # 根据商品ID获取商品价格
        """
        :param price_url: 商品价格URL
        :param no: 商品价格
        """
        price_url = "https://p.3.cn/prices/mgets?"
        # 拼接正确的链接
        full_url = price_url + "skuIds=" + sku_id[0]
        # print(full_url)
        price_data = requests.get(full_url,headers=headers)
        prices = json.loads(price_data.text)
        price = prices[0]["p"] # 获取当前价格

        #获取商品图片
        imgsrc = content.xpath('.//div[@class="product-intro clearfix"]/div[@class="preview-wrap"]/div[@class="preview"]/div[@class="jqzoom main-img"]/img/@data-origin')
        img =imgsrc[0]
        # print(imgsrc)
        # print(
        #     list_name,
        #     img[0],
        #     price
        #       )


        # 将获取的数据存入数据库
        #     连接数据库
        conn = pymysql.connect(host='localhost',user ='root', password ='174214',database ='commodity',charset ='utf8')
        cur = conn.cursor()
        into = "INSERT INTO commodity(productname,productimg,productprice) VALUES (%s,%s,%s)"
        values = (list_name,img,price)
        cur.execute(into, values)
        conn.commit()
        print('添加成功！')


if __name__ == '__main__':
    stratPage = int(input("请输入起始页:"))
    endPage = int(input("请输入结束页:"))
    #首页url
    # url = "https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8"
    url = "https://search.jd.com/Search?keyword=%E5%9E%83%E5%9C%BE%E6%A1%B6&enc=utf-8"
    #jd_spider  分页抓取
    jd_spider(url,stratPage,endPage)




