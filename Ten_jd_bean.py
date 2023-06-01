""" PagerMaid module Ten_jd_bean """

from pagermaid.enums import Client, Message
from pagermaid.listener import listener, _lock
from datetime import datetime
from urllib.parse import unquote_plus
from collections import defaultdict
import time
import datetime
import requests
import asyncio
import aiohttp
import re

# 青龙连不到调用
cokie = ''
cookie = []
lowest = 10

def update_lowest(new_value):
    global lowest
    lowest = new_value

async def ql_ck():
    try:
        # 青龙地址
        url = ''
        id = ''
        secret = ''

        async with aiohttp.ClientSession() as session:
            tourl = f'{url}/open/auth/token?client_id={id}&client_secret={secret}'
            async with session.get(tourl) as response:
                repo = await response.json()
            token = repo['data']['token']

            url = f'{url}/open/envs?searchValue=&t=1663653065698'
            headers = {'Authorization': f'Bearer {token}'}
            async with session.get(url, headers=headers, timeout=60) as response:
                repost = await response.json()

            cookie_list = []
            for i in repost['data']:
                if str(i['name']) == str('JD_COOKIE'):
                    if str(i['status']) == str('0'):
                        cookie.append(i['value'])
    except:
        print('获取青龙COOKIE失败,意外退出')


async def interrup_request(day_time, ck,):
    page = 0
    beans = True
    data = []
    async with aiohttp.ClientSession() as session:
        while beans:
            page = page + 1
            url = f'https://bean.m.jd.com/beanDetail/detail.json?page={page}'
            headers = {
                'User-Agent': "Mozilla/5.0 (Linux; Android 12; SM-G9880) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36 EdgA/106.0.1370.47",
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': ck,
            }
            body = '`body={"pageSize": "20", "page": page.toString()}&appid=ld'
            async with session.post(url, headers=headers, data=body, timeout=60) as response:
                interrupt_request = await response.json()
            if int(interrupt_request['code']) != int(0):
                return interrupt_request
            for i in interrupt_request['jingDetailList']:
                date = i['date']
                eventMassage = i['eventMassage']
                amount = i['amount']
                datetime = time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S"))
                if datetime >= day_time:
                    msg = [date, eventMassage, amount]
                    data.append(msg)
                elif datetime < day_time:
                    beans = False
    return data

def pt_pin(cookie):
    try:
        pt_pin = re.compile(r'pt_pin=(.*?);').findall(cookie)[0]
        pt_pin = unquote_plus(pt_pin)
    except IndexError:
        pt_pin = re.compile(r'pin=(.*?);').findall(cookie)[0]
        pt_pin = unquote_plus(pt_pin)
    return pt_pin

async def data_process(data):
    data = sorted([[item[0].split(" ")[1], item[1].split("[")[1].split("]")[0] if "[" in item[1] else item[1],int(item[2])] for item in data], reverse=True)
    jala = ''
    jaala = ''
    overdue = 0
    for item in data:
        item[0] = item[0][-8:]
    data = sorted(data, key=lambda x: int(x[2]), reverse=True)

    temp_dict = defaultdict(int)
    for item in data:
        temp_dict[item[1]] += int(item[2])
    processed_data = [[k, v] for k, v in temp_dict.items()]
    processed_data = sorted(processed_data, key=lambda x: x[1], reverse=True)
    total_reward = sum([item[1] for item in processed_data])
    msg = "{:<5} {:<5} {:<1}".format("奖励", '次数', "活动")
    for item in processed_data:
        count = sum([1 for x in data if x[1] == item[0]])
        if int(item[1]) >= int(lowest):
            mse = "{:<6} {:<6} {:<1}".format(f'{item[1]}豆', count, item[0])
            jala += mse + "\n"
        elif int(item[1]) < 0:
            mse = "{:<6} {:<6} {:<1}".format(f'{item[1]}豆', count, item[0])
            jaala += mse + "\n"
            overdue = overdue + abs(item[1])
    if len(jaala) > 1:
        msg = f'{total_reward+overdue}京豆(扣除过期或使用:{total_reward}京豆)\n\n{msg}\n{jala}\n过期或消费豆子:\n{jaala}\n'
        
    else:
        msg = f'{total_reward}京豆\n\n{msg}\n{jala}\n\n'
    return msg


@listener(command="by",description="查询本月豆子",parameters="<by id>")
async def bean(message: Message, bot: Client):
    try:
        if message.reply_to_message:
            text = message.reply_to_message.text
        else:
            text = message.arguments
        if not text:
            return await message.edit("出错了呜呜呜 ~ 没有成功获取到消息！")
        else:
            await message.edit("正在查询中.....")
        today = datetime.date.today()
        this_month_first_day = today.replace(day=1)
        this_month_first_day_zero = int(time.mktime(this_month_first_day.timetuple()))
        await ql_ck()
        if len(cookie) >= 1:
            ck = cookie[int(text) - int(1)]
        else:
            ck = cokie
            await message.edit("未从QL获取到COOKIE 调用默认COOKIE")
        data = await interrup_request(this_month_first_day_zero, ck)
        if 'code' in data and data['code'] != 0:
            await message.edit(f'{data}')
            await asyncio.sleep(5)
            await bot.delete_messages(message.chat.id, message.id)
        else:
            msg = await data_process(data)
            await message.edit(f'本月收入：{msg}本条信息将在30秒后自动销毁...')
            await asyncio.sleep(30)
            await bot.delete_messages(message.chat.id, message.id)
    except Exception as e:
        await message.edit(f'出现错误了 555 自动退出了哦.....{e}')



@listener(command="bz",description="查询本周豆子",parameters="<bz id>")
async def bean(message: Message,bot: Client):
    try:
        if message.reply_to_message:
            text = message.reply_to_message.text
        else:
            text = message.arguments
        if not text:
            return await message.edit("出错了呜呜呜 ~ 没有成功获取到消息！")
        else:
            await message.edit("正在查询中.....")
        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())
        monday_zero = int(time.mktime(monday.timetuple()))
        await ql_ck()
        if len(cookie) >= 1:
            ck = cookie[int(text) - int(1)]
        else:
            ck = cokie
            await message.edit("未从QL获取到COOKIE 调用默认COOKIE")
        data = await interrup_request(monday_zero, ck)
        if 'code' in data and data['code'] != 0:
            await message.edit(f'{data}')
            await asyncio.sleep(5)
            await bot.delete_messages(message.chat.id, message.id)
        else:
            msg = await data_process(data)
            await message.edit(f'本周收入：{msg}本条信息将在30秒后自动销毁...')
            await asyncio.sleep(30)
            await bot.delete_messages(message.chat.id, message.id)

    except Exception as e:
        await message.edit(f'出现错误了 555 自动退出了哦.....{e}')

@listener(command="b7", description="查近7天豆", parameters="<b7 id>")
async def bean(message: Message, bot: Client):
    try:
        if message.reply_to_message:
            text = message.reply_to_message.text
        else:
            text = message.arguments
        if not text:
            return await message.edit("出错了呜呜呜 ~ 没有成功获取到消息！")
        else:
            await message.edit("正在查询中.....")
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=6)
        seven_days_ago_zero = int(time.mktime(seven_days_ago.timetuple()))
        await ql_ck()
        if len(cookie) >= 1:
            ck = cookie[int(text) - int(1)]
        else:
            ck = cokie
            await message.edit("未从QL获取到COOKIE 调用默认COOKIE")
        data = await interrup_request(seven_days_ago_zero, ck)
        if 'code' in data and data['code'] != 0:
            await message.edit(f'{data}')
            await asyncio.sleep(5)
            await bot.delete_messages(message.chat.id, message.id)
        else:
            msg = await data_process(data)
            await message.edit(f'近七日收入：{msg}本条信息将在30秒后自动销毁...')
            await asyncio.sleep(30)
            await bot.delete_messages(message.chat.id, message.id)

    except Exception as e:
        await message.edit(f'出现错误了 555 自动退出了哦.....{e}')
@listener(command="b30", description="查近7天豆", parameters="<b7 id>")
async def bean(message: Message, bot: Client):
    try:
        if message.reply_to_message:
            text = message.reply_to_message.text
        else:
            text = message.arguments
        if not text:
            return await message.edit("出错了呜呜呜 ~ 没有成功获取到消息！")
        else:
            await message.edit("正在查询中.....")
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=29)
        seven_days_ago_zero = int(time.mktime(seven_days_ago.timetuple()))
        await ql_ck()
        if len(cookie) >= 1:
            ck = cookie[int(text) - int(1)]
        else:
            ck = cokie
            await message.edit("未从QL获取到COOKIE 调用默认COOKIE")
        data = await interrup_request(seven_days_ago_zero, ck)
        if 'code' in data and data['code'] != 0:
            await message.edit(f'{data}')
            await asyncio.sleep(5)
            await bot.delete_messages(message.chat.id, message.id)
        else:
            msg = await data_process(data)
            await message.edit(f'近30日收入：{msg}本条信息将在30秒后自动销毁...')
            await asyncio.sleep(30)
            await bot.delete_messages(message.chat.id, message.id)

    except Exception as e:
        await message.edit(f'出现错误了 555 自动退出了哦.....{e}')

@listener(command="b",description="查豆",parameters="<b id>")
async def bean(message: Message,bot: Client):
        if message.reply_to_message:
            text = message.reply_to_message.text
        else:
            text = message.arguments
        if not text:
            return await message.edit("出错了呜呜呜 ~ 没有成功获取到消息！")
        else:
            await message.edit("正在查询中.....")
        today = datetime.date.today()
        today_zero = int(time.mktime(today.timetuple()))
        await ql_ck()
        if "-" in text:
            mesid = {}
            key = 0
            text = text.split("-")
            for i in range(int(text[0]), int(text[1]) + 1):
                ck = cookie[int(i) - int(1)]
                data = await interrup_request(today_zero, ck)
                msg = await data_process(data)
                await bot.delete_messages(message.chat.id, message.id)
                cat = await bot.send_message(message.chat.id,f'第{i}账号 今日收入：{msg}本条信息将在8秒后自动销毁...')
                key = key + 1
                mesid[key] = {'catid': cat.chat.id, 'msgid': cat.id}

            await asyncio.sleep(8)
            for i in mesid:
                await bot.delete_messages(mesid[i]['catid'], mesid[i]['msgid'])
        else:
            ck = cookie[int(text) - int(1)]
            data = await interrup_request(today_zero, ck)
            if 'code' in data and data['code'] != 0:
                await message.edit(f'{data}')
                await asyncio.sleep(5)
                await bot.delete_messages(message.chat.id, message.id)
            else:
                msg = await data_process(data)
                await message.edit(f'今日收入：{msg}本条信息将在7秒后自动销毁...')
                await asyncio.sleep(7)
                await bot.delete_messages(message.chat.id, message.id)



@listener(command="low",description="设置最低查豆",parameters="<lowest 数量>")
async def bean(message: Message,bot: Client):
    try:
        if message.reply_to_message:
            text = message.reply_to_message.text
        else:
            text = message.arguments
        if not text:
            return await message.edit("出错了呜呜呜 ~ 没有成功获取到消息！")
        else:
            update_lowest(text)
            await message.edit(f"已设置最低查豆为 {lowest} 京豆")
            await asyncio.sleep(5)
            await bot.delete_messages(message.chat.id, message.id)

    except Exception as e:
        await message.edit(f'出现错误了 555 自动退出了哦.....{e}')