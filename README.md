<!--
 * @Author         : anlen123
 * @Date           : 2022-02-15 00:00:00
 * @LastEditors    : anlen123
 * @LastEditTime   : 2022-02-15 00:00:00
 * @Description    : None
 * @GitHub         : https://github.com/anlen123/nonebot_plugin_pixiv
-->

<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# nonebot_plugin_pixiv

_✨ NoneBot pixiv.net查询图片插件(支持多图和动图) ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/cscs181/QQ-Github-Bot/master/LICENSE">
    <img src="https://img.shields.io/github/license/cscs181/QQ-Github-Bot.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-pixiv">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-pixiv.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
</p>

## 使用方式
pixiv pid

例如：

pixiv 233

pixiv 1000

pixivRank 1
日榜

pixivRank 7 
周榜

pixivRank 30
月榜

直接发这种连接也能直接识别发送图片

https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)



## 配置
一共有四个配置项目


IMGROOT=/root/

AIOHTTP=http://127.0.0.1:1081

FFMPEG=/usr/bin/ffmpeg

PIXIV_COOKIES=xxx

PIXIV_R18=True

BAN_PIXIV_R18=[]

分别是:

1.保存图片的根目录

2.http代理地址

3.ffmpeg地址(不配置这个不支持动图)

4.你的p站的cookies (不配置不支持R18)

5.是否支持R18 （默认支持）

6.如果PIXIV_R18为True的情况下，设置黑名单（群号）

PS： R18支持两种配置方式

PIXIV_R18=True # 为所有群启用R18

PIXIV_R18=False # 不启用R18

PIXIV_R18=["123", "456"] #只为群123 和 群456启用r18



## 安装
pip install nonebot-plugin-pixiv

## 使用
nonebot.load_plugin('nonebot_plugin_pixiv')


# 已适配nonebot beta版本
