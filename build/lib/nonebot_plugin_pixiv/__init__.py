import nonebot
from typing import List
from nonebot.rule import Rule
from nonebot.plugin import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment, GroupMessageEvent
import aiohttp, re, os, random, cv2, asyncio, base64, json

global_config = nonebot.get_driver().config
config = global_config.dict()

imgRoot = config.get('imgroot') if config.get('imgroot') else f"{os.environ['HOME']}/"
proxy_aiohttp = config.get('aiohttp') if config.get('aiohttp') else ""
pixiv_cookies = config.get('pixiv_cookies') if config.get('pixiv_cookies') else ""
ffmpeg = config.get('ffmpeg') if config.get('ffmpeg') else "/usr/bin/ffmpeg"
headersCook = {
    'referer': 'https://www.pixiv.net',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
}
if pixiv_cookies:
    headersCook['cookie'] = pixiv_cookies

pixiv_r18 = config.get('pixiv_r18')
if not pixiv_r18:
    pixiv_r18 = True
if pixiv_r18 and ( pixiv_r18 == 'True' or pixiv_r18 == 'False'):
    pixiv_r18 = eval(pixiv_r18)
elif pixiv_r18:
    try:
        pixiv_r18 = eval(pixiv_r18)
        if not isinstance(pixiv_r18,list):
            print("配置错误！！pixiv_r18应该是列表")
        else:
            for x in pixiv_r18:
                if not(isinstance(x,int) or (isinstance(x,str) and str(x).isdigit())):
                    print("配置错误！！pixiv_r18中应该是int类型或者str的数值类型")
    except:
        print("配置错误！！")
    

pathHome = f"{imgRoot}QQbotFiles/pixiv"
if not os.path.exists(pathHome):
    os.makedirs(pathHome)

pathZipHome = f"{imgRoot}QQbotFiles/pixivZip"
if not os.path.exists(pathZipHome):
    os.makedirs(pathZipHome)

def isPixivURL() -> Rule:
    async def isPixivURL_(bot: "Bot", event: "Event") -> bool:
        if event.get_type() != "message":
            return False
        msg = str(event.get_message())
        if re.findall("https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)", msg):
            return True
        return False

    return Rule(isPixivURL_)


pixivURL = on_message(rule=isPixivURL())

async def check_r18(bot: Bot,event : Event, pid: str)->bool:
    print("R18检查ing")
    if not await pan_R18(pid):
        return True
    if isinstance(pixiv_r18,bool):
        if (not pixiv_r18):
            await bot.send(event=event,message="不支持R18，请修改配置后操作！")
            return False
    elif isinstance(pixiv_r18, list):
        if isinstance(event, GroupMessageEvent):
            flag = any(True if str(x) == str(event.group_id) else False for x in pixiv_r18)
            if not flag:
                await bot.send(event=event,message="不支持R18，请修改配置后操作！")
            return flag

    return True

@pixivURL.handle()
async def pixivURL(bot: Bot, event: Event):
    pid = re.findall("https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)", str(event.get_message()))
    if pid:
        pid = [x for x in pid[0] if x][0]
        if not check_r18(bot,event,pid):
            return
        xx = (await checkGIF(pid))
        if xx != "NO":
            await GIF_send(xx, pid, event, bot)
        else:
            await send(pid, event, bot)


pixiv = on_regex(pattern="^pixiv\ ")


@pixiv.handle()
async def pixiv_rev(bot: Bot, event: Event):
    pid = str(event.message).strip()[6:].strip()
    print("?????????????????????")
    if not await check_r18(bot,event,pid):
        return
    xx = (await checkGIF(pid))
    print("动图判断")
    if xx != "NO":
        await GIF_send(xx, pid, event, bot)
    else:
        await send(pid, event, bot)


async def fetch(session, url, name):
    print("发送请求：", url)
    async with session.get(url=url, headers=headersCook, proxy=proxy_aiohttp) as response:
        # async with session.get(url=url, headers=headers) as response:
        async def fetch(session, url, name):
            print("发送请求：", url)
            async with session.get(url=url, headers=headersCook, proxy=proxy_aiohttp) as response:
                # async with session.get(url=url, headers=headers) as response:
                code = response.status
                if code == 200:
                    content = await response.content.read()
                    with open(f"{imgRoot}QQbotFiles/pixiv/" + name, mode='wb') as f:
                        f.write(content)
                    return True
                return False


async def main(PID):
    # url = f"https://www.pixiv.net/artworks/{PID}"
    url = f"https://api.obfs.dev/api/pixiv/illust?id={PID}"
    async with aiohttp.ClientSession() as session:
        x = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        content = await x.content.read()
        content = json.loads(content)
        # down_url = re.findall('"original":"(.*?)\.(png|jpg|jepg)"', content.json())
        if content.get('error'):
            return
        url = content.get('illust').get('meta_single_page')
        if url:
            url = url.get('original_image_url')
        else:
            url = content.get('illust').get('meta_pages')[0].get('image_urls').get('original')
        print(url)
        name = url[url.rfind("/") + 1:]
        hou_zhui = name.split(".")[1]
        print(name)
        print(hou_zhui)
        names = []
        num = 1
        if os.path.exists(f"{imgRoot}QQbotFiles/pixiv/" + name):
            while os.path.exists(f"{imgRoot}QQbotFiles/pixiv/" + name) and num <= 6:
                names.append(name)
                newstr = f"_p{num}.{hou_zhui}"
                num += 1
                name = re.sub("_p(\d+)\.(png|jpg|jepg)", newstr, name)
                print(name)
        else:
            while (await fetch(session=session, url=url, name=name) and num <= 6):
                names.append(name)
                newstr = f"_p{num}.{hou_zhui}"
                num += 1
                url = re.sub("_p(\d+)\.(png|jpg|jepg)", newstr, url)
                name = url[url.rfind("/") + 1:]
        return names


async def getImgsByDay(url):
    async with aiohttp.ClientSession() as session:
        if url == 'day':
            url = 'https://www.pixiv.net/ranking.php'
        else:
            url = f'https://www.pixiv.net/ranking.php?mode={url}'
        # response = await session.get(url=url,headers=headers)
        response = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        text = (await response.content.read()).decode()
        imgs = set(re.findall('\<a href\=\"\/artworks\/(.*?)\"', text))
        return list(imgs)


pixivRank = on_regex(pattern="^pixivRank\ ")


@pixivRank.handle()
async def pixiv_rev(bot: Bot, event: Event):
    info = str(event.message).strip()[10:].strip()
    dic = {
        "1": "day",
        "7": "weekly",
        "30": "monthly"
    }
    if info in dic.keys():
        imgs = random.choices(await getImgsByDay(dic[info]), k=5)
        names = []
        for img in imgs:
            names.append(await main(img))
        if not names:
            await bot.send(event=event, message="发生了异常情况")
        else:
            msg = None
            for name in names:
                if name:
                    for t in name:
                        path = f"{imgRoot}QQbotFiles/pixiv/{t}"
                        size = os.path.getsize(path)
                        if size // 1024 // 1024 >= 10:
                            await yasuo(path)
                        msg += MessageSegment.image(await base64_path(path))
            try:
                if isinstance(event, GroupMessageEvent):
                    await send_forward_msg_group(bot, event, 'qqbot', msg)
                else:
                    await bot.send(event=event, message=msg)
            except:
                await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查")
    else:
        await bot.send(event=event, message=Message("参数错误\n样例: 'pixivRank 1' , 1:day,7:weekly,30:monthly"))


async def base64_path(path: str):
    ff = "空"
    with open(path, "rb") as f:
        ff = base64.b64encode(f.read()).decode()
    return f"base64://{ff}"


async def send(pid: str, event: Event, bot: Bot):
    names = await main(pid)
    if not names:
        await bot.send(event=event, message="没有这个pid的图片")
    else:
        msg = None
        for name in names:
            path = f"{imgRoot}QQbotFiles/pixiv/{name}"
            size = os.path.getsize(path)
            if size // 1024 // 1024 >= 10:
                await yasuo(path)
            msg += MessageSegment.image(await base64_path(path))
        try:
            if isinstance(event, GroupMessageEvent):
                await send_forward_msg_group(bot, event, 'qqbot', msg)
            else:
                await bot.send(event=event, message=msg)

        except:
            await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查,尝试一张一张的发图片ing")
            try:
                for name in names:
                    path = f"{imgRoot}QQbotFiles/pixiv/{name}"
                    size = os.path.getsize(path)
                    if size // 1024 // 1024 >= 10:
                        await yasuo(path)
                    await bot.send(event=event, message=MessageSegment.image(await base64_path(path)))
            except:
                try:
                    await bot.send(event=event, message="一张一张发送图片也风控了，尝试修改md5值再发送")
                    for name in names:
                        path = f"{imgRoot}QQbotFiles/pixiv/{name}"
                        os.system(f"echo '1' >> {path}")
                    msg=None
                    for name in names:
                        path = f"{imgRoot}QQbotFiles/pixiv/{name}"
                        size = os.path.getsize(path)
                        if size // 1024 // 1024 >= 10:
                            await yasuo(path)
                        msg += MessageSegment.image(await base64_path(path))
                    if isinstance(event, GroupMessageEvent):
                        await send_forward_msg_group(bot, event, 'qqbot', msg)
                    else:
                        await bot.send(event=event, message=msg)
                except:
                    await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查!!!")


async def yasuo(path):
    while os.path.getsize(path) // 1024 // 1024 >= 10:
        image = cv2.imread(path)
        shape = image.shape
        res = cv2.resize(image, (shape[1] // 2, shape[0] // 2), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f"{path}", res)


async def checkGIF(pid: str) -> str:
    url = f'https://www.pixiv.net/ajax/illust/{pid}/ugoira_meta'
    async with aiohttp.ClientSession() as session:
        if pixiv_cookies:
            headersCook['cookie'] = pixiv_cookies
        x = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        content = await x.json()
        print(content)
        if content['error']:
            return "NO"
        return content['body']['originalSrc']


async def GIF_send(url: str, pid: str, event: Event, bot: Bot):
    path_pre = f"{imgRoot}QQbotFiles/pixivZip/{pid}"
    if os.path.exists(f"{path_pre}/{pid}.gif"):
        size = os.path.getsize(f"{path_pre}/{pid}.gif")
        while size // 1024 // 1024 >= 15:
            msg = await run(f"file {path_pre}/{pid}.gif")
            cheng = int(msg.split(" ")[-3]) // 2
            kuan = int(msg.split(" ")[-1]) // 2
            await run(f"{ffmpeg} -i {path_pre}/{pid}.gif -s {cheng}x{kuan} {path_pre}/{pid}_temp.gif")
            await run(f"rm -rf {path_pre}/{pid}.gif")
            await run(f"mv {path_pre}/{pid}_temp.gif {path_pre}/{pid}.gif")
            size = os.path.getsize(f"{path_pre}/{pid}.gif")
        try:
            await bot.send(event=event, message=MessageSegment.image(await base64_path(f"{path_pre}/{pid}.gif")))
        except:
            await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查")
        return
    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        code = response.status
        if code == 200:
            content = await response.content.read()
            if not os.path.exists(f"{path_pre}.zip"):
                with open(f"{path_pre}.zip", mode='wb') as f:
                    f.write(content)
                if not os.path.exists(f"{path_pre}"):
                    os.mkdir(f"{path_pre}")
            await run(f"unzip -n {path_pre}.zip -d {path_pre}")
            image_list = sorted(os.listdir(f"{path_pre}"))
            await run(f"rm -rf {path_pre}.zip")
            await run(f"{ffmpeg} -r {len(image_list)} -i {path_pre}/%06d.jpg {path_pre}/{pid}.gif -n")
            # 压缩
            size = os.path.getsize(f"{path_pre}/{pid}.gif")
            while size // 1024 // 1024 >= 15:
                msg = await run(f"file {path_pre}/{pid}.gif")
                cheng = int(msg.split(" ")[-3]) // 2
                kuan = int(msg.split(" ")[-1]) // 2
                await run(f"{ffmpeg} -i {path_pre}/{pid}.gif -s {cheng}x{kuan} {path_pre}/{pid}_temp.gif")
                await run(f"rm -rf {path_pre}/{pid}.gif")
                await run(f"mv {path_pre}/{pid}_temp.gif {path_pre}/{pid}.gif")
                size = os.path.getsize(f"{path_pre}/{pid}.gif")
            try:
                await bot.send(event=event, message=MessageSegment.image(await base64_path(f"{path_pre}/{pid}.gif")))
            except:
                await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查")


async def run(cmd: str):
    print(cmd)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    return (stdout + stderr).decode()


# 合并消息
async def send_forward_msg_group(
        bot: Bot,
        event: GroupMessageEvent,
        name: str,
        msgs: List[str],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": bot.self_id, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )


async def pan_R18(PID):
    print("判断是不是R18")
    url = f"https://api.obfs.dev/api/pixiv/illust?id={PID}"
    async with aiohttp.ClientSession() as session:
        x = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        content = await x.content.read()
        content = json.loads(content)
        if content.get('error'):
            return False
        tag = content['illust']['tags'][0]['name']
        print("tag: "+tag)
        if tag == 'R-18':
            return True
        else:
            return False

# pixivS = on_regex(pattern="^来点")


# @pixivS.handle()
        # x = await session.get(url="https://www.pixiv.net/ajax/search/artworks/"+str(key), headers=headersCook, proxy=proxy_aiohttp)
        # # x = await session.get(url=url, headers=headers)
        # content = await x.content.read()
        # content = json.loads(content)
        # print(content['error'])
        # if not content['error']:
            # if content['body']['illustManga']['data']:
                # pid = random.choice(content['body']['illustManga']['data'])['id']
    # if pid:
        # xx = (await checkGIF(pid))
        # if xx != "NO":
            # await GIF_send(xx, pid, event, bot)
        # else:
            # await send(pid, event, bot)
    # else:
        # await bot.send(event=event,message="抱歉！没有搜索到任何内容")
