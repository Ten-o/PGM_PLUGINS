# -*- coding: utf-8 -*-
""" PagerMaid module Ten_jd_bean """

from pagermaid.utils import lang, alias_command, obtain_message, client
from pagermaid.listener import listener
from pagermaid.utils import alias_command
from collections import defaultdict
import time
import datetime
import asyncio
import aiohttp
cookie = []


# 青龙连不到调用cokie
cokie = 'pt_key=123123123;pt_pin=123123;'

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
                        cookie_list.append(i['value'])
            return cookie_list
    except:
        print('获取青龙COOKIE失败,意外退出')

async def interrup_request(day_time, text):
    page = 0
    beans = True
    data = []
    cookie = await ql_ck()
    ind = int(text) - int(1)
    if len(cookie) >= 1:
        ck = cookie[ind]
        rat = 0
    else:
        ck = cookie
        rat = 1
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
                    msg = 0
    return data, rat


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
        if int(item[1]) >= 50:
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


@listener(is_plugin=False, outgoing=True, command=alias_command("by"),
          description="<查豆>",
          parameters="<by id>")
async def bean(context):
    try:
        try:
            text = await obtain_message(context)
        except ValueError:
            return await context.edit("出错了呜呜呜 ~ 没有成功获取到消息！")
        else:
            await context.edit("正在查询中.....")
        today = datetime.date.today()
        this_month_first_day = today.replace(day=1)
        this_month_first_day_zero = int(time.mktime(this_month_first_day.timetuple()))
        data, rat = await interrup_request(this_month_first_day_zero, int(text))
        if rat == 1:
            await context.edit("未从QL获取到COOKIE 调用默认COOKIE")
        msg = await data_process(data)
        await context.edit(f'本月收入：{msg}本条信息将在30秒后自动销毁...')
        await asyncio.sleep(30)
        await context.delete()

    except Exception as e:
        await context.edit(f'出现错误了 555 自动退出了哦.....{e}')


@listener(is_plugin=False, outgoing=True, command=alias_command("bz"),
          description="<查豆>",
          parameters="<bz id>")
async def bean(context):
    try:
        try:
            text = await obtain_message(context)
        except ValueError:
            return await context.edit("出错了呜呜呜 ~ 没有成功获取到消息！")
        else:
            await context.edit("正在查询中.....")
        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())
        monday_zero = int(time.mktime(monday.timetuple()))
        data, rat = await interrup_request(monday_zero, int(text))
        if rat == 1:
            await context.edit("未从QL获取到COOKIE 调用默认COOKIE")
        msg = await data_process(data)
        await context.edit(f'本周收入：{msg}本条信息将在30秒后自动销毁...')
        await asyncio.sleep(30)
        await context.delete()

    except Exception as e:
        await context.edit(f'出现错误了 555 自动退出了哦.....{e}')

@listener(is_plugin=False, outgoing=True, command=alias_command("b7"),
          description="<查豆>",
          parameters="<b7 id>")
async def bean(context):
    try:
        try:
            text = await obtain_message(context)
        except ValueError:
            return await context.edit("出错了呜呜呜 ~ 没有成功获取到消息！")
        else:
            await context.edit("正在查询中.....")
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=6)
        seven_days_ago_zero = int(time.mktime(seven_days_ago.timetuple()))
        data, rat = await interrup_request(seven_days_ago_zero, int(text))
        if rat == 1:
            await context.edit("未从QL获取到COOKIE 调用默认COOKIE")
        msg = await data_process(data)
        await context.edit(f'近7日收入：{msg}本条信息将在30秒后自动销毁...')
        await asyncio.sleep(30)
        await context.delete()

    except Exception as e:
        await context.edit(f'出现错误了 555 自动退出了哦.....{e}')

@listener(is_plugin=False, outgoing=True, command=alias_command("b"),
          description="<查豆>",
          parameters="<b id>")
async def bean(context):
    try:
        try:
            text = await obtain_message(context)
        except ValueError:
            return await context.edit("出错了呜呜呜 ~ 没有成功获取到消息！")
        else:
            await context.edit("正在查询中.....")
        today = datetime.date.today()
        today_zero = int(time.mktime(today.timetuple()))
        data, rat = await interrup_request(today_zero, int(text))
        if rat == 1:
            await context.edit("未从QL获取到COOKIE 调用默认COOKIE")
        msg = await data_process(data)
        await context.edit(f'今日收入：{msg}本条信息将在10秒后自动销毁...')
        await asyncio.sleep(10)
        await context.delete()

    except Exception as e:
        await context.edit(f'出现错误了 555 自动退出了哦.....{e}')
