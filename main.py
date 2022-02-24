# -*- coding: utf-8 -*-
import time
from datetime import datetime
import requests


def get_res():
    current_time = int(round(time.time() * 1000))
    url = 'https://www.jisilu.cn/data/cbnew/pre_list/?___jsl=LST___t={}'.format(
        current_time)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',

    }

    res = requests.post(url, headers=headers)
    return res.json()


def make_info(data, today):
    data_by_type = {u'上市': [], u'申购': []}
    for row in data['rows']:
        cell = row['cell']
        zz_status = cell['progress_nm']
        if u'上市' not in zz_status and u'申购' not in zz_status:
            continue

        zz_time = zz_status[:10] + ' 23:00:00'
        if datetime.strptime(zz_time, '%Y-%m-%d %H:%M:%S') < today:
            continue

        data_by_type[zz_status[10:12]].append(
            {'name': cell['bond_nm'], 'time': zz_status[:10],
             'rt': cell['pma_rt']}
        )

    return data_by_type


def make_msg(data_by_type):
    msg = u'<p>最近可申购{}只可转债</p>'.format(len(data_by_type[u'申购']))
    if data_by_type[u'申购']:
        msg += u'<ul>{}</ul>'.format(''.join(
            [u'<li>{} {} {}%</li>'.format(x['name'], x['time'], x['rt']) for x
             in data_by_type[u'申购']]))

    msg += u'<p>最近上市{}只可转债</p>'.format(len(data_by_type[u'上市']))
    if data_by_type[u'上市']:
        msg += u'<ul>{}</ul>'.format(''.join(
            [u'<li>{} {} {}%</li>'.format(x['name'], x['time'], x['rt']) for x
             in data_by_type[u'上市']]))

    return msg


def send_msg(token, content):
    url = 'http://www.pushplus.plus/send'
    res = requests.post(url, data={
        'token': token,
        'title': u'可转债提醒',
        'content': content,
        'template': 'json',
        'topic': 'my'
    })
    return res.text


if __name__ == '__main__':
    import sys
    import traceback

    token = sys.argv[1]
    today = datetime.now()

    try:
        data = get_res()
    except:
        send_msg(token, u'<p>可转债接口请求出错</p>')
        quit()

    try:
        data_by_type = make_info(data, today)
    except:
        send_msg(token, traceback.format_exc().replace('\n', '<br>'))
        quit()

    msg = make_msg(data_by_type)

    send_msg(token, msg)
