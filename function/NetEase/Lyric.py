#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import re
import requests

NCMLyricApi = 'http://music.163.com/api/song/lyric?lv=-1&tv=-1&id='
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}


def getNCMLyric(data):
    isUrl = re.findall(
        "(http[s]?:\/\/music.163.com\/.*\?[^\w]*id=(\d+).*)|\s*(\d+)\s*", data)

    try:
        if(isUrl[0][0]):
            res = json.loads(requests.get(
                url=NCMLyricApi + isUrl[0][1], headers=headers).text)
        else:
            res = json.loads(requests.get(
                url=NCMLyricApi + isUrl[0][2], headers=headers).text)
        return res
    except IndexError:
        pass
