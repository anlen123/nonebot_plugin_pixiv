from pathlib import Path

import nonebot
from nonebot import run
import nonebot
from nonebot.rule import Rule
from nonebot.plugin import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, Message
import aiohttp
import re
import os
import random
import cv2
import asyncio
_sub_plugins = set()
_sub_plugins |= nonebot.load_plugins(
    str((Path(__file__).parent / "plugins").
    resolve()))

global_config = nonebot.get_driver().config
config = global_config.dict()

imgRoot=config.get('imgroot') if config.get('imgroot') else f"{os.environ['HOME']}/"
proxy_aiohttp = config.get('aiohttp') if config.get('aiohttp') else ""
pixiv_cookies = config.get('pixiv_cookies') if config.get('pixiv_cookies') else ""
ffmpeg = config.get('ffmpeg') if config.get('ffmpeg') else "/usr/bin/ffmpeg"

pathHome = imgRoot+"QQbotFiles/pixiv" 
if not os.path.exists(pathHome):
    os.makedirs(pathHome)

pathZipHome = imgRoot+"QQbotFiles/pixivZip" 
if not os.path.exists(pathZipHome):
    os.makedirs(pathZipHome)

headersCook = {
    'referer': 'https://www.pixiv.net',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
}

if pixiv_cookies:
    headersCook['cookie']  = pixiv_cookies

async def checkConfig(bot: Bot,event: Event) -> bool:
    if not pixiv_cookies:
        await bot.send(event=event,message="pixiv_cookies未配置!!")
        return False
    elif not proxy_aiohttp:
        await bot.send(event=event,message="proxy_aiohttp未配置!!")
        return False
    return True
    

def isPixivURL() -> Rule:
    async def isPixivURL_(bot: "Bot", event: "Event") -> bool:
        if event.get_type() != "message":
            return False
        msg = str(event.get_message())
        if re.findall("https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)", msg):
            return True
        return False
    return Rule(isPixivURL_)

pixivURL= on_message(rule=isPixivURL())

@pixivURL.handle()
async def pixivURL(bot: Bot, event: Event):
    if not await checkConfig(bot,event):
        return
    pid = re.findall("https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)", str(event.get_message()))
    if pid:
        pid = [x for x in pid[0] if x][0]
        xx = (await checkGIF(pid))
        if xx!="NO":
            await GIF_send(xx,pid,event,bot)
        else:
            await send(pid,event,bot)


pixiv = on_regex(pattern="^pixiv\ ")
@pixiv.handle()
async def pixiv_rev(bot: Bot, event: Event):
    if not await checkConfig(bot,event):
        return
    pid = str(event.message).strip()[6:].strip()
    xx = (await checkGIF(pid))
    if xx!="NO":
        await GIF_send(xx,pid,event,bot)
    else:
        await send(pid,event,bot)



async def fetch(session, url, name):
    print("发送请求：", url)
    async with session.get(url=url, headers=headersCook,proxy=proxy_aiohttp) as response:
    # async with session.get(url=url, headers=headers) as response:
        code = response.status
        if code ==200:
            content = await response.content.read()
            with open(f"{imgRoot}QQbotFiles/pixiv/"+name, mode='wb') as f:
                f.write(content)
            return True
        return False

async def main(PID):
    url = f"https://www.pixiv.net/artworks/{PID}"
    async with aiohttp.ClientSession() as session:
        x = await session.get(url=url, headers=headersCook,proxy=proxy_aiohttp)
        # x = await session.get(url=url, headers=headers)
        content = await x.content.read()
        down_url = re.findall('"original":"(.*?)\.(png|jpg|jepg)"', content.decode())
        if not down_url:
            return ""
        url = '.'.join(down_url[0])
        name = url[url.rfind("/")+1:]
        num= 1
        names = []
        if os.path.exists(f"{imgRoot}QQbotFiles/pixiv/"+name):
            hou = down_url[0][1]
            while os.path.exists(f"{imgRoot}QQbotFiles/pixiv/"+name) and num<=6:
                names.append(name)
                newstr = f"_p{num}.{hou}"
                num+=1
                name = re.sub("_p(\d+)\.(png|jpg|jepg)",newstr,name)
        else:
            hou = down_url[0][1]
            while ( await fetch(session=session,url=url,name=name) and num<=6):
                names.append(name)
                newstr= f"_p{num}.{hou}"
                num+=1
                url = re.sub("_p(\d+)\.(png|jpg|jepg)",newstr,url)
                name = url[url.rfind("/")+1:]
        return names


async def getImgsByDay(url):
    async with aiohttp.ClientSession() as session:
        if url=='day':
            url = 'https://www.pixiv.net/ranking.php'
        else:
            url = f'https://www.pixiv.net/ranking.php?mode={url}'
        # response = await session.get(url=url,headers=headers)
        response = await session.get(url=url,headers=headersCook,proxy=proxy_aiohttp)
        text = (await response.content.read()).decode()
        imgs = set(re.findall('\<a href\=\"\/artworks\/(.*?)\"', text))
        return list(imgs)

pixivRank = on_regex(pattern="^pixivRank\ ")

@pixivRank.handle()
async def pixiv_rev(bot: Bot, event: Event):
    if not await checkConfig(bot,event):
        return
    info = str(event.message).strip()[10:].strip()
    dic={
        "1":"day",
        "7":"weekly",
        "30":"monthly"
    }
    if info in dic.keys():
        imgs = random.choices(await getImgsByDay(dic[info]),k=5)
        names = []
        for img in imgs:
            names.append(await main(img))
        if not names :
            await bot.send(event=event,message="发生了异常情况")
        else:
            msg = ""
            for name in names:
                if name:
                    for t in name:
                        size = os.path.getsize(f"{imgRoot}QQbotFiles/pixiv/{t}")
                        if size//1024//1024>=10:
                            await yasuo(f"{imgRoot}QQbotFiles/pixiv/{t}")
                        msg+=f"[CQ:image,file=file:///{imgRoot}QQbotFiles/pixiv/{t}]"
            await bot.send(event=event,message=Message(msg))
    else:
        await bot.send(event=event,message=Message("参数错误\n样例: 'pixivRank 1' , 1:day,7:weekly,30:monthly"))    


async def send(pid:str,event:Event,bot:Bot):
    names = await main(pid)
    if not names :
        await bot.send(event=event,message="没有这个pid的图片")
    else:
        msg = ""
        for name in names:
            size = os.path.getsize(f"{imgRoot}QQbotFiles/pixiv/{name}")
            if size//1024//1024>=10:
                await yasuo(f"{imgRoot}QQbotFiles/pixiv/{name}")
            msg+=f"[CQ:image,file=file:///{imgRoot}QQbotFiles/pixiv/{name}]"
        await bot.send(event=event,message=Message(msg))

async def yasuo(path):
    while os.path.getsize(path)//1024//1024>=10:
        image=cv2.imread(path)
        shape= image.shape
        res = cv2.resize(image, (shape[1]//2,shape[0]//2), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f"{path}",res)

async def checkGIF(pid:str)->str:
    url = f'https://www.pixiv.net/ajax/illust/{pid}/ugoira_meta'
    async with aiohttp.ClientSession() as session:
        x = await session.get(url=url, headers=headersCook,proxy=proxy_aiohttp)
        content = await x.json()
        if content['error']:
            return "NO"
        return content['body']['originalSrc']
            
async def GIF_send(url:str,pid:str,event:Event,bot:Bot):
    p = f"{imgRoot}QQbotFiles/pixivZip/{pid}"
    print(os.path.exists(f"{p}/{pid}.gif"))
    if os.path.exists(f"{p}/{pid}.gif"):
        size = os.path.getsize(f"{p}/{pid}.gif")
        while size//1024//1024>=15:
            # await bot.send(event=event,message="图片太大了,发不出来")
            msg = await run(f"file {p}/{pid}.gif")
            cheng = int(msg.split(" ")[-3])//2
            kuan = int(msg.split(" ")[-1])//2
            await run(f"{ffmpeg} -i {p}/{pid}.gif -s {cheng}x{kuan} {p}/{pid}_temp.gif")
            await run(f"rm -rf {p}/{pid}.gif")
            await run(f"mv {p}/{pid}_temp.gif {p}/{pid}.gif")
            size = os.path.getsize(f"{p}/{pid}.gif")
        await bot.send(event=event,message=Message(f"[CQ:image,file=file:///{p}/{pid}.gif]"))
        return
    async with aiohttp.ClientSession() as session:
        response= await session.get(url=url, headers=headersCook,proxy=proxy_aiohttp)
        code = response.status
        if code ==200:
            content = await response.content.read()
            if not os.path.exists(f"{p}.zip"):
                with open(f"{p}.zip", mode='wb') as f:
                    f.write(content)
                if not os.path.exists(f"{p}"):
                    os.mkdir(f"{p}")
            await run(f"unzip -n {p}.zip -d {p}")
            image_list = sorted(os.listdir(f"{p}"))
            await run(f"rm -rf {p}.zip")
            await run(f"{ffmpeg} -r {len(image_list)} -i {p}/%06d.jpg {p}/{pid}.gif -n")
            # 压缩
            size = os.path.getsize(f"{p}/{pid}.gif")
            while size//1024//1024>=15:
                # await bot.send(event=event,message="图片太大了,发不出来")
                msg = await run(f"file {p}/{pid}.gif")
                cheng = int(msg.split(" ")[-3])//2
                kuan = int(msg.split(" ")[-1])//2
                await run(f"{ffmpeg} -i {p}/{pid}.gif -s {cheng}x{kuan} {p}/{pid}_temp.gif")
                await run(f"rm -rf {p}/{pid}.gif")
                await run(f"mv {p}/{pid}_temp.gif {p}/{pid}.gif")
                size = os.path.getsize(f"{p}/{pid}.gif")

            await bot.send(event=event,message=Message(f"[CQ:image,file=file:///{p}/{pid}.gif]"))

async def run(cmd:str):
    print(cmd)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    return (stdout+stderr).decode()
