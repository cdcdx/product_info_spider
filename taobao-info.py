#coding=utf-8

import re
import urllib
import urllib2
import cookielib
import StringIO, gzip
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36' }

#解压gzip  
def gzdecode(data) :  
    compressedstream = StringIO.StringIO(data)  
    gziper = gzip.GzipFile(fileobj=compressedstream)    
    data2 = gziper.read()   # 读取解压缩后数据   
    return data2 

#获取html代码
def getHtml(url):
    request = urllib2.Request(url , headers = headers)
    try:
        response = urllib2.urlopen(request)
        html = response.read()
        return html
    except urllib2.URLError,e:
        print e.reason

#目录是否存在，不存在则创建
def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        if os.path.isfile(path):
            os.mkdir(path)

#提取描述url
def descUrl(html):
    reg = r"descUrl.*?location.protocol==='http:' \? '//(.*?)'.?:"
    desurlre = re.compile(reg,re.I)
    desurl = re.findall(desurlre , html)
    return desurl

#提取所有图片imglist
def getImglist(html):
    reg = r'src=\"(.*?)\"'
    imgre = re.compile(reg,re.I)
    imglist = re.findall(imgre , html)
    return imglist

#保存所有图片imglist
def saveImgTo(imglist, path):
    createDir(path)
    imgIndex = 1
    for imgurl in imglist:
        splist = imgurl.split('.')
        filetype = splist[len(splist)-1]
        print "saving " + imgurl
        imgurl = 'http:' + imgurl
        print imgurl
        try:
            urllib.urlretrieve(imgurl , path + "/info-"+ str(imgIndex) + '.' + filetype )
            imgIndex += 1
            print "==> ok!"
        except:
            print "==> err!!!!!!"

#提取主图
def getMainImg(html, path):
    createDir(path)
    reg = r'auctionImages.*?\[(.*?)\]'
    imgre = re.compile(reg,re.I)
    titleImg = re.findall(imgre , html)
    titleImg = titleImg[0]
    imglist = titleImg.split(',')
    titleIndex = 1
    for imgurl in imglist:
        print "img ==== >  " + imgurl
        imgurl = imgurl.strip('"')
        imgurl = 'http:' + imgurl
        print imgurl
        splist = imgurl.split('.')
        filetype = splist[len(splist)-1]
        try:
            urllib.urlretrieve(imgurl , path + "/main-"+ str(titleIndex) + '.' + filetype )
            titleIndex += 1
            print "==> ok!"
        except:
            print "==> err!!!!!!"

#获取宝贝参数
def parse_html_info(html, savePath):
    
    #PATTERN_title = r'<title>(.*?)</title>'
    #pat = re.compile(PATTERN_title,re.S)
    #info_name = pat.findall(html)[0]
    #print(info_name)
    #info_title = info_name.split('-')[0]
    #print(info_title)
    
    #PATTERN = r'<!-- attributes div start -->(.*?)</div>'
    PATTERN_attributes = r'<ul class="attributes-list">(.*?)</ul>'
    pat = re.compile(PATTERN_attributes,re.S)
    attributes_list = pat.findall(html)[0]
    #print(result)
    
    #output = open( savePath+"/"+info_title+".htm" , "w")
    output = open( savePath+"/url-info.htm" , "w")
    output.write('<ul class="attributes-list">')
    output.write(attributes_list)
    output.write('</ul>')
    output.close()

#从一个淘宝页面，得到详情图片
def getTaoBaoImg(url, savePath):
    html = getHtml(url)
    #print html
    #output = open( savePath+"/url-html.htm" , "w")
    #output.write(html)
    #output.close()
    
    #获取淘贝参数
    #html_copy = html
    #parse_html_info(html_copy, savePath)
    
    #获取淘贝主图
    getMainImg(html, savePath)
    
    print "----------------------------------------------------------"
    desurl = descUrl(html)
    desurl = "http://" + desurl[0]
    #print "desurl = " + desurl
    #得到淘贝详情html
    desHtml = getHtml(desurl)
    #print desHtml
    output = open( savePath+"/url-desHtml.htm" , "w")
    output.write(desHtml)
    output.close()
    
    #得到淘贝详情Imglist
    imglist = getImglist(desHtml)
    #print imglist
    output = open( savePath+"/url-imglist.htm" , "w")
    output.write(str(imglist))
    output.close()
    
    #下载淘贝详情Img
    saveImgTo(imglist , savePath)

#-------------------------------------我是华丽的分界线 begin Other-----------------------------------------

#提取其他详情图片列表
def getOtherImgurllist(html):
    reg = r'src="(.*?)"'
    desre = re.compile(reg,re.S)
    imgurllist = re.findall(desre , html)
    return imgurllist

#从其他提取详情图片
def getOtherImg(url, savePath):
    html = getHtml(url)
    imglist = getOtherImgurllist(html)
    saveImgTo(imglist , savePath)

#提取其他主图
def getOthertitleImg(html, savePath):
    print "todo:"

#-------------------------------------我是华丽的分界线 end Other-----------------------------------------

#保存原地址
def saveUrl(url , savePath):
    output = open( savePath + "/url.htm" , "w")
    output.write("""<html>
<head>
<meta http-equiv="Content-Language" content="zh-CN">
<meta HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=gb2312">
<meta http-equiv="refresh" content="0.1;url=""" + url + """\">
<title></title>
</head>
<body>
</body>
</html>""")
    output.close()

#主函数
def main():
    url_txt = "url.txt"
    if len(sys.argv)>1 and sys.argv[1]:
        url_txt = sys.argv[1]
    input = open(url_txt, 'r')
    urls = input.read( )
    urls = urls.split('\n')
    print urls

    savepath = "taobao-img"
    if len(sys.argv)>2 and sys.argv[2]:
        savepath = sys.argv[2]
    #print savepath

    urlIndex = 1
    for url in urls:
        if len(url) < 10:
            continue
        
        print "\n\n----------------------------------------------------------"
        print(url)
        
        #id值
        id_value = str(urlIndex)
        #解析id
        values = url.split('?')[-1]
        for key_value in values.split('&'):
            #print  key_value.split('=')
            if key_value.split('=')[0] == 'id':
                #print key_value.split('=')[1]
                id_value = key_value.split('=')[1]
        #解析shopId
        #解析title
        #parse_title(url, savePath):
        html = getHtml(url)
        
        #解析shopId
        PATTERN_shopId = r'data-shopid="(.*?)"></div>'
        pat = re.compile(PATTERN_shopId, re.S)
        shopId_value = pat.findall(html)[0]
        print(shopId_value)
        
        #解析title
        PATTERN_title = r'<title>(.*?)</title>'
        pat = re.compile(PATTERN_title, re.S)
        info_name = pat.findall(html)[0]
        print(info_name)
        info_title = info_name.split('-')[0]
        #print(info_title)
        info_title = eval(repr(info_title).replace('/', ''))
        print(info_title)
        '''
        #创建目录
        urlSavePath = savepath +'/'+ shopId_value +'-'+ id_value +'-'+ info_title
        createDir(urlSavePath)
        #print urlSavePath name="current_price" value= "
        '''
        #解析产品价格 current_price
        PATTERN_price = r'name="current_price" value= "(.*?)"/>'
        pat = re.compile(PATTERN_price,re.S)
        current_price = pat.findall(html)[0]
        print(current_price)
        
        #解析产品参数 attributes-list
        #PATTERN = r'<!-- attributes div start -->(.*?)</div>'
        PATTERN_attributes = r'<ul class="attributes-list">(.*?)</ul>'
        pat = re.compile(PATTERN_attributes,re.S)
        attributes_list = pat.findall(html)[0]
        #print(attributes_list)
        
        #解析产品名称
        PATTERN_product = ur'品名:&nbsp;(.*?)</li>'
        #print(PATTERN_product)
        #attributes_list_gb = unicode(attributes_list, 'gb2312')
        attributes_list_gb = unicode(attributes_list, 'gbk')
        #print(attributes_list_gb)
        pat = re.compile(PATTERN_product, re.S)
        product_name_gb = pat.findall(attributes_list_gb)
        #print(product_name_gb)
        if product_name_gb==[] :
            product_name = []
        else:
            #product_name = product_name_gb[0].encode('gb2312')
            product_name = product_name_gb[0].encode('gbk')
        print(product_name)
        
        #解析产品品类
        PATTERN_class = ur'品类:&nbsp;(.*?)</li>'
        #print(PATTERN_class)
        #attributes_list_gb = unicode(attributes_list, 'gb2312')
        attributes_list_gb = unicode(attributes_list, 'gbk')
        #print(attributes_list_gb)
        pat = re.compile(PATTERN_class, re.S)
        product_class_gb = pat.findall(attributes_list_gb)
        #print(product_class_gb)
        if product_class_gb==[] :
            product_class = []
        else:
            #product_class = product_class_gb[0].encode('gb2312')
            product_class = product_class_gb[0].encode('gbk')
        product_class = eval(repr(product_class).replace('/', ''))
        print(product_class)
        
        #SaveName
        SaveName = ''
        if product_class!=[] :
            SaveName = product_class +'-'
        if product_name!=[] :
            SaveName = SaveName + product_name +'-'
        
        #创建目录 
        urlSavePath = ''
        if SaveName == '' :
            urlSavePath = savepath +'/'+ current_price +'-'+ info_title +'-'+ shopId_value +'-'+ id_value 
        else:
            urlSavePath = savepath +'/'+ SaveName + current_price +'-'+ info_title +'-'+ shopId_value +'-'+ id_value 
        #urlSavePath = ''
        #if len(product_name)>30 :
        #    urlSavePath = savepath +'/'+ current_price +'-'+ info_title +'-'+ shopId_value +'-'+ id_value 
        #elif product_name==[] :
        #    urlSavePath = savepath +'/'+ current_price +'-'+ info_title +'-'+ shopId_value +'-'+ id_value 
        #else:
        #    urlSavePath = savepath +'/'+ product_name +'-'+ current_price +'-'+ info_title +'-'+ shopId_value +'-'+ id_value 
        print urlSavePath
        if not os.path.exists(urlSavePath):
            createDir(urlSavePath)
        else:
            continue
        
        #保存参数网页
        output = open( urlSavePath+"/"+info_title+".htm" , "w")
        output.write('<ul class="attributes-list">')
        output.write(attributes_list)
        output.write('</ul>')
        output.close()
        
        #保存网页
        saveUrl(url, urlSavePath)
        print '*'*50+' '+urlSavePath
        print 'url = '+url
        print ''
        
        #GetImg
        if url.find('taobao') != -1:
            getTaoBaoImg(url, urlSavePath)
        else:
            getOtherImg(url, urlSavePath)
        urlIndex += 1
    print "success!"

if __name__ == "__main__":
    main()