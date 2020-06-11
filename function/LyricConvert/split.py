#!/usr/bin/python
# -*- coding: utf-8 -*-  
import sys
import re

def convert(ori_txt):
    vrc_obj = {
        'karaoke': False,
        'scrollDisabled': False,
        'origin': {
            'version': 2,
            'text': ''
        },
        'translate': {
            'version': 2,
            'text': ''
        }
    }

    pattern = re.compile(r'(\[.*?\])\s*([^\[\]]*)\s*')
    matches = pattern.findall(ori_txt)
    for time_stamp, lrc in matches:
        lrc = lrc.strip().split('\n')
        vrc_obj['origin']['text'] += time_stamp + lrc[0] + '\n'
        if len(lrc) > 1:
            vrc_obj['translate']['text'] += time_stamp + lrc[1] + '\n'

    return vrc_obj