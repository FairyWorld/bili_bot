# -*- coding: utf-8 -*-
import requests, json, re, time, os
from BiliClient import Article

import timeout_decorator

@timeout_decorator.timeout(3600)
def start():
    #获取secrets里的cookie
    cookies = {
        "SESSDATA": os.environ.get('SESSDATA', None),
        "bili_jct": os.environ.get('BILI_JCT', None)
    }

    num = 8 #只爬取8张图,可以调大，如果中间网络异常会丢失几张图，最终数量可能达不到

    #创建B站专栏
    article = Article(cookies, "美女手机壁纸") #创建B站专栏草稿,并设置标题
    content = article.Content() #创建content类编写文章正文
    content.startP().add('所有图片均转载于').startB().add('网络').endB().add('，如有侵权请联系我，我会立即').startB().add('删除').endB().endP().br()
        #开始一段正文    添加正文           开始加粗  加粗文字  结束加粗                                                           结束一段文字  换行

    #下面开始爬取P站图片
    session = requests.session()
    session.trust_env = True
    session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4280.88 Safari/537.36",
                "Referer": ""
                })
    picList = session.get("http://service.picasso.adesk.com/v1/vertical/category/4e4d610cdf714d2966000000/vertical?limit=10&order=new").json()["res"]["vertical"]
    imageUrl = ''
    for i in range(num):
        url = picList[i]["img"]
        try:
            #关闭ssl校验
            res = session.get(url, verify=False)
            imageUrl = article.imageFile2Url(res.content) #这里上传到B站，得到图片链接
            print(f'获取第{i+1}张图片成功：{imageUrl}')
        except:
            continue
        title = f'图片{i+1}'
        content.startP().startB().add(f'{i+1}.').endB().endP().picUrl(imageUrl, title) #将图片链接插入文章内容
                        #序号加粗                            插入图片链接(站内图片链接)和图片标题
        print(f'第{i+1}张图片插入文章成功')
        time.sleep(3)

    try:
        article.setImage(imageUrl)  #将最后一张图片设置为专栏缩略图
        article.setCategory(4)  #将专栏分类到"动画 → 动漫杂谈"
        article.setOriginal(0)  #设置为非原创专栏,因为是转载的
        article.setTags("电脑壁纸,手机壁纸,壁纸,动漫美图,美图,Pixiv,美女,二次元,动漫,动画") #设置tags标签
        article.save() #保存专栏至B站草稿箱
        print('保存草稿成功')
        article.submit() #发布专栏，注释掉后需要到article.getAid(True)返回的网址去草稿箱手动提交
        print('发表专栏成功')
    except:
        print('发表专栏失败')

start()
