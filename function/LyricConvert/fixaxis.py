#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

def fixlrcs(origin, translated):
    """
    :param origin: string, lrc text with origin language
    :param translated: string, lrc text with translated language
    :return: 2 strings, origin and fixed translated lrc text

    使翻译版本和原文版本的lrc时轴对应。以原文版本为主，翻译版本中原本无时轴的位置补空轴，多余的时轴去除。
    """
    pattern = re.compile(r'(\[.*?\])\s*([^\[\]]*)')
    ori_matches = pattern.findall(origin)
    trans_matches = pattern.findall(translated)

    trans_dict = dict(trans_matches)
    fixed_trans = ''
    for time_stamp, ori_lrc in ori_matches:
        fixed_trans += time_stamp + (trans_dict[time_stamp] if time_stamp in trans_dict else '\n')

    return origin, fixed_trans
