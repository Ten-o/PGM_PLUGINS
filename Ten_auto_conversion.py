import re
import redis
from urllib import parse
from pagermaid.listener import listener
from pagermaid.enums import Client, Message


#推送
CHAT_IDS  = []
#黑名单
blacklist_IDS = []

#redis 去重 60秒
pool = redis.ConnectionPool(host='10.10.10.0', port=6379, decode_responses=True, db=3, password='')
r = redis.Redis(connection_pool=pool)

LOREAL_TYPE = {
        '10006': {'name': '邀请入会', 'script': 'jd_loreal_invite'},
        }

WX_TYPE = {
    'wxTeam': {'name': '组队瓜分', 'variable': 'M_WX_TEAM_URL','script': 'jd_wx_Team', 'type': '1'},
}


def get_activity_info(text):
    result = re.findall(r'((http|https)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])', text)
    if len(result) <= 0:
        return None, None
    url = re.search('((http|https)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])', text)[0]
    params = parse.parse_qs(parse.urlparse(url).query)
    ban_rule_list = [
        'activityId',
        'giftId',
        'actId',
        'tplId',
        'token',
        'code',
        'a',
        'id']
    activity_id = None
    for key in ban_rule_list:
        activity_id = params.get(key)
        if activity_id is not None:
            activity_id = params.get(key)
            activity_id = activity_id[0]
            break
    return activity_id, url



@listener(outgoing=True,ignore_edited=True, incoming=True)
async def process_keyword(message: Message, bot: Client):
    for i in blacklist_IDS:
        if int(message.chat.id) == int(i):
            return f'进入屏蔽黑名单 {message.chat.id}'
    activateId = get_activity_info(message.text)
    url = str(activateId[1])
    async def TG_CHID(msg):
        if len(msg) > 10:
            if r.hget('url', f'{activateId[0]}') == None:
                for i in CHAT_IDS:
                    await bot.send_message(int(i),f'{msg}\n\n🚗活动地址:{url}\n\n🚀：线报来自：{message.chat.title}')
                print(f'推送成功:{url}')
                value = {f'{activateId[0]}': f'{url}'}
                s = r.hmset('url', value)
                r.expire('url', 60)
                print(f'写入数据库成功:{s},{url}')
            else:
                print(f'数据库已存在:{url}')

    if re.findall('activityType=([\w]{5})', url, re.S):
        for i in LOREAL_TYPE:
            type = re.findall('activityType=([\w]{5})', url, re.S)
            if int(type[0]) == int(i):
                script = LOREAL_TYPE[f'{i}']['script']
                msg = f'export {script}="{url}"'
                await TG_CHID(msg)
    else:
        for i in WX_TYPE:
            if re.findall(f'{i}', url, re.S):
                if int(WX_TYPE[i]['type']) == 1:
                    msg = f'export ' + WX_TYPE[i][f'variable'] + f'="{url}"'
                    await TG_CHID(msg)
                elif int(WX_TYPE[i]['type']) == 0:
                    msg = f'export ' + WX_TYPE[i][f'variable'] + f'="{activateId[0]}"'
                    await TG_CHID(msg)
