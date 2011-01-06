#!/usr/bin/env python
#coding: UTF-8
'''
@file: report.py
@author: breaddawson@gmail.com
@brief: auto publish weather report to twitter.
        Weather Infos fetched from www.weather.com.cn
        Twitter API from Python Twitter Tools(http://mike.verdone.ca/twitter/)

@history

0.7: 11/01/06 Added reply according to city name in mention
              For example, @itianqi beijing 
0.6: 11/01/05 Support OAuth
              Automatically reply mentions with latest weather report 
0.5: 09/12/18 Added weather report for Guangzhou (weatehr_GZ)
0.4: 09/07/08 Fixed a bug that emoji out of index
0.3: 09/06/21 Added realtime details for today, such as current temperature, wind strength, etc.
              Thanks jjgod@newsmth for realtime info source.
0.2: 09/06/20 Include emoji!!! support. For example, a cloud icon will be inserted if it's cloudy.
0.1: 09/06/20 First edition. 
'''

import urllib, os, sys, time
import os.path
from oauth_dance import oauth_dance
from api import Twitter, TwitterHTTPError
from oauth import OAuth, read_token_file
import random
from datetime import datetime, tzinfo, timedelta
import time
from lunardate import LunarDate

def _py26OrGreater():
    import sys
    return sys.hexversion > 0x20600f0

if _py26OrGreater():
    import json
else:
    import simplejson as json
    
def lunar_today():
    day1=["初", "十", "廿", "三"]
    day2=["十", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    month=day2[:]
    month[1] = "正"
    month.extend(["十", "冬", "腊"])
    return "%s月%s%s" % (month[LunarDate.today().month],
                       day1[LunarDate.today().day/10],
                       day2[LunarDate.today().day%10])


class GMT8(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=8)
    def tzname(self, dt):
        return "GMT +800"
    def dst(self, dt):
        return timedelta(0)


def get_weather(citycode="101010100", cityname=u'北京', debug=True):
    
    if debug:
        print "[Debug] Getting weather"

    #citycode = "101010100" # beijing
    fore_url = "http://m.weather.com.cn/data/%s.html" % (citycode) # forecast in 3 days(including today)
    rt_url = "http://www.weather.com.cn/data/sk/%s.html" % (citycode) # today's realtime

    forecast = urllib.urlopen(fore_url).read()
    realtime = urllib.urlopen(rt_url).read()

    #data = json.loads(urllib.urlopen(urlname).read())["weatherinfo"]

    # record all weather infos in order to debug
    logpath = "./"
    f = open(logpath+"weather.log", "a+")
    f.write(time.ctime()+"\n"+forecast+"\n" + "[Realtime]\n" + realtime)

    forecast = json.loads(forecast)["weatherinfo"]
    realtime = json.loads(realtime)["weatherinfo"]

    # 今天是2009年6月20日，星期六，农历五月廿八
    # 今日多云转阴 34℃~21℃
    # 当前@12:00 28.1℃  北风<3级 湿度31%
    
    # forecast:
    # 公历日期: "date_y"
    # 农历日期："date"
    # 星期：     "week"
    # 天气：     "weather1"
    # 天气图标: "img1" "img2"
    # index: 0-晴 1-多云 2-阴 3-雨? 4-雷阵雨
    # emoji: \ue04a-晴 \ue049-多云 \ue04d-阴天 \ue04b-雨 \ue33a-雪(冰淇淋) 
    # 温度：     "temp1"

    # realtime:
    # 时间: "time" "12:00"
    # 温度: "temp" "28.1"
    # 风向: "WD"   "北风"
    # 风力: "WS"   "小于3级"
    # 风力': "WSE" "<3"
    # 风速: "sm"   "1.9"
    # 湿度: "SD"   "31%"

    #print report
    emoji = {"0":u'\ue04a', "1":u'\ue049', "2":u'\ue04d', "3":u'\ue04b', "4":u'\ue04b', "5":u'\ue04b', "6":u'\ue04b', "7":u'\ue04b', "8":u'\ue04b', "14":u'\ue33a', "99":''}
    report_today = u"今天是%s,%s,农历%s \n%s今日%s%s%s %s\n%s实况 %s℃ %s%s级 湿度%s" % \
            (forecast["date_y"], forecast["week"],  #forecast["date"], \
             lunar_today().decode("utf-8"), \
             cityname, \
            forecast["weather1"], emoji[forecast["img1"]], emoji[forecast["img2"]], forecast["temp1"],\
            realtime["time"], realtime["temp"], realtime["WD"], realtime["WSE"], realtime["SD"])
    #print report_today

    report_future = u"未来两天天气状况:\n明天 %s%s%s %s,\n后天 %s%s%s %s" % \
            (forecast["weather2"], emoji[forecast["img3"]], emoji[forecast["img4"]], forecast["temp2"],\
             forecast["weather3"], emoji[forecast["img5"]], emoji[forecast["img6"]], forecast["temp3"])
    #print report_future

    report_today = report_today.replace(u"\u2103", u"度")
    report_today = report_today.replace(u"~", u"至")
    report_future = report_future.replace(u"\u2103", u"度")
    report_future = report_future.replace(u"~", u"至")
    
    f.close()
    
    return report_today, report_future

def get_twitter(debug=False):
    # This is secret and key of my app "ibread"
    # this is set up on twitter.com
    CONSUMER_KEY = "NXdiUFv7ZqhO5Ojr8GocA"
    CONSUMER_SECRET = "CMRgb7BHpHLlcZ0NqHF06pWbFtv1zPqV98KTaFxV2YQ"
    #oauth_filename = os.environ.get('HOME', '') + os.sep + '.my_twitter_oauth'
    oauth_filename = sys.path[0] + os.sep + 'my_twitter_oauth'
    
    if debug:
        print oauth_filename
    
    # if did not found the auth file, create one
    if not os.path.exists(oauth_filename):
        oauth_dance("ibread", CONSUMER_KEY, CONSUMER_SECRET, oauth_filename)

    oauth_token, oauth_token_secret = read_token_file(oauth_filename)
    
    if debug:
        print oauth_token, oauth_token_secret

    tw = Twitter(
        auth=OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET),
        secure=True,
        api_version='1',
        domain='api.twitter.com')
    
    return tw


def get_code_dict():
    '''
        Return hanzi dict and pinyin dict
    '''
    dict_file = sys.path[0] + os.sep + "city_code.dat" 
    try:
        f = open(dict_file)
    except IOError:
        print "Error openning %s" % dict_file
        return None
    
    city_pinyin_dict= {} # beijing: 北京
    code_dict = {}
    
    for line in f:
        hanzi, pinyin, code = map(lambda x: x.strip(), line.split())
        code_dict[hanzi.decode('utf8')] = code
        code_dict[pinyin] = code  
        city_pinyin_dict[pinyin] = hanzi.decode('utf8')

    return code_dict, city_pinyin_dict

def update(tweets="", debug=False):
    
    tw = get_twitter()
    
    points = [0000, 800, 1200, 1800]
    report_today, report_future = get_weather()

    # get dictionary city => code
    code_dict, city_pinyin_dict = get_code_dict()
    
    # set up log file
    logpath = sys.path[0] + os.sep
    f = open(logpath+"weather.log", "a+")

    last_id_file = logpath+"last_id.dat"
    try:
        last_id = int(open(last_id_file).readline().strip())
    except IOError, ValueError:
        last_id = 0L
        
    count = 30 # check latest 10 mentions every time
    period = 0.5*60 # check mention every 1 minute
    
    while True:
        curtime = datetime.now(tz=GMT8())
        hour, min, sec = curtime.hour, curtime.minute, curtime.second
        
        hourmin = hour*100+min

        if debug:
            print "[Debug] Curtime: %s" % curtime
            print "[Debug] hourmin: %s" % hourmin
        
        # update the report at certain time points
        if hourmin % 30 == 0:
            report_today, report_future = get_weather()

        # check mentions and reply back
        if True:
            try:
                mentions = tw.statuses.replies(count=count)
            except:
                print "Error when getting replies"
                print sys.exc_info()
                continue
            
            for m in mentions:
                # Already replied, do nothing                
                if m['id'] == last_id:
                    if debug:
                        print "Already checked this mention: %s" % m['text']
                    break
                
                target = m['user']['screen_name']
                text = m['text']
                
                if not text.startswith('@itianqi'):
                    continue
                
                text = text.split()[1].strip()
                
                no_chinese = True
                for t in text:
                    if ord(t) > 255:
                        no_chinese = False
                        break
                
                if no_chinese:
                    text = text.lower()
                
                if text in code_dict.keys():
                    citycode = code_dict[text]
                    cityname = no_chinese and city_pinyin_dict[text] or text
                    report_today, report_future = get_weather(citycode=citycode, cityname = cityname)
                    try:
                        now_time = curtime.strftime("%H:%M:%S")
                        msg = "Reply to %s @%s B %s" % (target, datetime.now(), text)
                        print msg.encode('utf8')
                        tw.statuses.update(status=u'@%s %s (%s)' % (target, report_future, now_time))
                        tw.statuses.update(status=u'@%s %s (%s)' % (target, report_today, now_time))
                    except:
                        print "Error when getting replies"
                        print sys.exc_info()
                else:
                   try:
                        tw.statuses.update(status=u'@%s 很抱歉，未找到您输入的城市"%s"。请用中文或拼音。如 北京 或 beijing'\
                         % (target, text))
                    except:
                        print "Error when getting replies"
                        print sys.exc_info()
                    
                
                f.write("Reply to %s @%s" % (target, datetime.now()))
            
            last_id = mentions[0]['id']
            # update last_id
            try: 
                open(last_id_file, "w").write(str(last_id))
            except IOError:
                print "[Debug] Error updating last_id"
            
        if hourmin in points:
            try:
                tw.statuses.update(status=report_future)
                #tw.statuses.update(status=report_future.encode("utf-8"))
                tw.statuses.update(status=report_today.encode("utf-8"))
                print "Twitter %s" % "weather report"
            except:
                print "Error when posting weather report"
                print sys.exc_info()
            
        time.sleep(period)
                
    f.close()
    
#    #x = tw.statuses.friends_timeline(count=10)
#    #for i in x:
#    #    pass
#    #    print i['user']['screen_name'], i['text']
#
#    #tw.statuses.update(status='facetime太爽了')
#    
#    x = tw.statuses.replies(count=10)
#    for i in x:
#        print i['user']['screen_name'], i['text']
#        print i['id'], i['in_reply_to_status_id']
#    
#    return
#
#
#    #tw = twitter.Twitter(config["account"], config["pass"])
#    if len(tweets)>1:
#        tw.statuses.update(status=tweets)
#        print "Twitter %s" % tweets
#    else:
#        #tw.statuses.update(status=u'哈哈哈')
#        tw.statuses.update(status=report_future)
#        #tw.statuses.update(status=report_future.encode("utf-8"))
#        tw.statuses.update(status=report_today.encode("utf-8"))
#        print "Twitter %s" % "weather report"

def update_imm():
    '''
        Update immediatelly
    '''
    tw = get_twitter()
    
    report_today, report_future = get_weather()

    tw.statuses.update(status=report_future)
    tw.statuses.update(status=report_today.encode("utf-8"))

if __name__ == "__main__":
    if len(sys.argv)==1:
        update()
    else:
        update(sys.argv[1])
