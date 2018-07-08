import sys
import re
import requests
from bs4 import BeautifulSoup
import argparse

helpMessage = \
'''
1:午前1日人間ドック 
2:午前健保指定ドック 
3:午後基本検診 
4:午後1日人間ドック 
5:午後健保指定ドック
'''

def GetTargetHtml(course=2):
    
    referer = 'https://www.its-kenpo.or.jp/kanri/chokuei/yoyaku/privacy_yoyaku_kojinyoyku.html'
    targetUrl = 'https://sy.its-kenpo.or.jp/kenshinyoyaku/indiv_rsv_inquire'

    payload = {
            '_method':'POST',
            'data[SearchSpace][cond_examination_year]':'2018',
            'data[SearchSpace][cond_course_single]':course,
            'data[SearchSpace][cond_option][1]':'0',
            'data[SearchSpace][cond_option][2]':'0',
            'data[SearchSpace][cond_option][3]':'0',
            }

    s = requests.Session()
    s.headers.update({'referer': referer})
    r = s.get(targetUrl)
    soup = BeautifulSoup(r.text, 'html.parser')

    data_token_key = soup.find(attrs={'name': 'data[_Token][key]'}).get('value')
    data_token_field = soup.find(attrs={'name': 'data[_Token][fields]'}).get('value')
    payload['data[_Token][key]'] = data_token_key
    payload['data[_Token][fields]'] = data_token_field

    r = s.post('https://sy.its-kenpo.or.jp/kenshinyoyaku/indiv_rsv_inquire/search_space#controls', data=payload)
    return r.text

def GetRawData(html):
    soup = BeautifulSoup(html, 'html.parser')
    # print(bool(soup.find(id="SearchSpaceSearchSpaceForm")))
    rawData = soup.find_all(href="#controls")
    return rawData

def NotReservedDateList(rawData):
    result = []
    for data in rawData:
        day = {}
        day['date'] = re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}', data['onclick'])[0]
        day['free'] = data.text
        result.append(day)
    return result

def main():

    # パーサの作成
    psr = argparse.ArgumentParser()
    psr.add_argument('-c', '--course', default='2', type=int, help=helpMessage)
    args = psr.parse_args()

    if int(args.course) > 5:
        print('--course option is under 5')
        sys.exit()

    targetHtml = GetTargetHtml(args.course)
    rawData = GetRawData(targetHtml)
    result = NotReservedDateList(rawData)

    print(result)

if __name__ == '__main__':
    main()
