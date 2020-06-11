#!/usr/bin/python
# -*- coding: utf-8 -*-  
import re

def mixlrc2vrc(ori_txt):
    """
    :param ori_txt: string, the original mixed-lrc text
    :return: object, the vrc-format lyric
    """
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

    pattern = re.compile(r'(\[.*?\])\s*([^\[\]]*)')
    matches = pattern.findall(ori_txt)
    for time_stamp, lrc in matches:
        lrc = lrc.strip().split('\n')
        vrc_obj['origin']['text'] += time_stamp + lrc[0] + '\n'
        vrc_obj['translate']['text'] += time_stamp + (lrc[1] if len(lrc) > 1 else '') + '\n'

    return vrc_obj


def lrcs2mixlrc(origin, translated):
    """
    :param origin: string, lrc text with origin language
    :param translated: string, lrc text with translated language
    :return: string, mixed-lrc text with origin language at first line and translated language at second line
    """
    pattern = re.compile(r'(\[.*?\])\s*([^\[\]]*)')
    ori_matches = pattern.findall(origin)
    trans_matches = pattern.findall(translated)

    trans_dict = dict(trans_matches)
    mixed_lrc = ''
    for time_stamp, ori_lrc in ori_matches:
        lrc = time_stamp + '\n' + ori_lrc + (trans_dict[time_stamp] if time_stamp in trans_dict else '\n')
        mixed_lrc += lrc

    return mixed_lrc


def vrc2mixlrc(vrc_obj):
    """
    :param vrc_obj: object, the vrc-format lyric
    :return: string, mixed-lrc text with origin language at first line and translated language at second line
    """
    ori, trans = vrc_obj['origin']['text'], vrc_obj['translate']['text']
    return lrcs2mixlrc(ori, trans)