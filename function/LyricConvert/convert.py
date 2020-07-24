import re


class ConvertError(Exception):
    pass


def mlrc2vrc(ori_txt):
    """
    :param ori_txt: string, the original mixed-lrc text
    :return: object, the vrc-format lyric
    """
    vrc_obj = {
        'karaoke': False,
        'scrollDisabled': False,
        'translated': False,
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
        if len(lrc) > 1:
            vrc_obj['translated'] = True
        vrc_obj['origin']['text'] += time_stamp + lrc[0] + '\n'
        vrc_obj['translate']['text'] += time_stamp + (lrc[1] if len(lrc) > 1 else '') + '\n'

    return vrc_obj


def lrcs2mlrc(origin, translated):
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


def vrc2mlrc(vrc_obj):
    """
    :param vrc_obj: object, the vrc-format lyric
    :return: string, mixed-lrc text with origin language at first line and translated language at second line
    """
    ori, trans = vrc_obj['origin']['text'], vrc_obj['translate']['text']
    return lrcs2mlrc(ori, trans)


def ass2vrc(ass_txt):
    """
    :param ass_txt: str, lyric in format of ass
    :return: object, the vrc-format lyric
    """
    vrc_obj = {
        'karaoke': False,
        'scrollDisabled': False,
        'translated': True,
        'origin': {
            'version': 2,
            'text': ''
        },
        'translate': {
            'version': 2,
            'text': ''
        }
    }

    lines = ass_txt.split('\n')
    targeted = 0  # state marker
    start_id = -1
    end_id = -1
    text_id = -1

    for idx, line in enumerate(lines):
        if line == '[Events]':
            targeted = 1
            continue
        if not targeted:
            continue
        
        line = line.replace(' ', '')  # erase spaces
        if len(line) == 0:
            continue  # empty line
        
        pos = line.find(':')
        items = line[pos + 1:]
        items = items.split(',')
        if targeted == 1:
            # find position for start, end, text.
            for i, attr in enumerate(items):
                if attr == 'Start':
                    start_id = i
                elif attr == 'End':
                    end_id = i
                elif attr == 'Text':
                    text_id = i
            if start_id == -1:
                raise ConvertError('Fail to find "Start" attribute in [Events]')
            if end_id == -1:
                raise ConvertError('Fail to find "End" attribute in [Events]')
            if text_id == -1:
                raise ConvertError('Fail to find "Text" attribute in [Events]')
            targeted = 2
        elif targeted == 2:
            start = items[start_id]
            end = items[end_id]  # not used for now
            text = items[text_id]
            text = text.split('\\N')
            if len(text) < 2:
                raise ConvertError('Fail to find translation in line {:d}'.format(idx))
            ori_txt, trans_txt = text[0], text[1]
            vrc_obj['origin']['text'] += '[{}]{}'.format(start, ori_txt)
            vrc_obj['translate']['text'] += '[{}]{}'.format(start, trans_txt)
    
    return vrc_obj
        