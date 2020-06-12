#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import re
import requests
import random
import time

QQMusicLyricApi = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5509.400 QQBrowser/10.1.1601.400"
]

headers = {
    'cookie': 'yqq_stat=0; pgv_pvi=6676326400; pgv_si=s7011130368; pgv_info=ssid=s5173118475; ts_last=y.qq.com/portal/player.html; pgv_pvid=9872308450; ts_uid=7899888096; userAction=1; yq_index=0; yq_playschange=0; yq_playdata=; player_exist=1; qqmusic_fromtag=66; yplayer_open=1',
    'origin': 'https://y.qq.com',
    'referer': 'https://y.qq.com/portal/player.html',
    'User-Agent': random.choice(USER_AGENTS),
}

jsond = {
    '-': 'MusicJsonCallback_lrc',
    'pcachetime': None,
    'songmid': None,
    'g_tk_new_20200303': 766058380,
    'g_tk': 879516080,
    'loginUin': 0,
    'hostUin': 0,
    'format': 'json',
    'inCharset': 'utf8',
    'outCharset': 'utf-8',
    'notice': 0,
    'platform': 'yqq.json',
    'needNewCode': 0
}


def getQQMLyric(data):
    
    pattern = r".*\/(\w+)\.html.*"
    match_obj = re.match(pattern, data)

    try:
        if match_obj:
            jsond["pcachetime"] = round(time.time() * 1000)
            jsond["songmid"] = match_obj.group(1)

            print(jsond)

            http = requests.get(QQMusicLyricApi, params=jsond, headers=headers)

            res = json.loads(http.text)
            print(http.headers)
        return res
    except (UnboundLocalError, IndexError, TypeError):
        pass
