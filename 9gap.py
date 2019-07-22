import os
import time
import requests
from urllib import request

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}
# 此url是用来爬取正文图片的
url1 = 'https://images-cdn.9gag.com/photo/aPYNV9G_700b.jpg'
pic = requests.get(url=url1,headers=headers).content
#a.jpg保存的就是正文图片
with open('./a.jpg','wb')as f:
    f.write(pic)

# 此url是用来爬取评论的baseurl
url2 = 'https://comment-cdn.9gag.com/v1/cacheable/comment-list.json'
#这边可以修改count来选取爬取的评论数量,因为页面评论随时都在更新,先爬了150条
count = 150
param = {
    "appId": "a_dd8f2b7d304a10edaf6f29517ea0ca4100a43d1b",
    "url": "http://9gag.com/gag/aPYNV9G",
    "count": count,
    "order": "score",
    "origin": "https://9gag.com",
}
if not os.path.exists('./Comments'):
    os.mkdir('./Comments')

if not os.path.exists('./picture'):
    os.mkdir('./picture')

if not os.path.exists('./picture/avatar'):
    os.mkdir('./picture/avatar')

if not os.path.exists('./picture/com_comment'):
    os.mkdir('./picture/com_comment')

#存放用户头像的链接地址
avatar_url_list = []
#存放评论里图片的链接地址
com_comment_list = []

#获取评论里的评论
def down(comment_id):
    sub_param=param
    sub_param["refCommentId"] = comment_id
    response = requests.get(url=url2,headers=headers,params=sub_param).json()
    comments_list = response['payload']['comments']
    return comments_list

#获取评论人的头像,姓名,评论时间,以及获取评论的评论
def get_value(comments_list,filetp):
    for comment in comments_list:
        com_content_url = ''
        avatar_url = comment['user']['avatarUrl']
        username = comment['user']['displayName']
        avatar_url_list.append(avatar_url)
        com_time = comment['timestamp']
        com_time = time.ctime(com_time)
        com_content = comment['text']
        if comment['type'] == 'userMedia':
            com_content_url = comment['media'][0]['imageMetaByType']['image']['url']
            com_content = com_content.replace(com_content_url,"")
            com_comment_list.append(com_content_url)
        if comment['children']:
            commend_id = comment['children'][0]['commentId']
            if comment['childrenTotal'] == 1:
                sub_comments_list = comment['children']
                get_value(sub_comments_list,filetp)
            elif comment['childrenTotal'] > 1:
                sub_comments_list = down(commend_id)
                get_value(sub_comments_list,filetp)
        if com_content_url:
            filetp.write('用户:' + username + ',发表内容:' + com_content +';评论图片地址:'+'./picutre/com_comment/%s'%(com_content_url.split('/')[-1])+ ',头像地址:' + './picutre/avatar/%s' % (avatar_url.split('/')[-1]) + ',评论时间:' + com_time + '\n')
        filetp.write('用户:'+ username+',发表内容:'+com_content+',头像地址:'+'./picutre/avatar/%s'%(avatar_url.split('/')[-1])+',评论时间:'+com_time+'\n')

#起始的访问请求
response = requests.get(url=url2,headers=headers,params=param).json()
comments_list = response['payload']['comments']
#user.text用来存放用户的信息
with open('./Comments/user.txt','w',encoding='utf-8')as f:
    get_value(comments_list,f)

#请求头像地址并下载保存
for avatar in avatar_url_list:
    img_name = avatar.split('/')[-1]
    img_path = './picture/avatar/'+ img_name
    img_url = avatar
    request.urlretrieve(img_url, img_path)

#请求评论图片地址并下载保存
for com in com_comment_list:
    img_name = com.split('/')[-1]
    img_path = './picture/com_comment/'+ img_name
    img_url = com
    request.urlretrieve(img_url, img_path)
