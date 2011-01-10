#!/usr/bin/env python
#coding: UTF-8
'''
@file: report.py
@author: breaddawson@gmail.com
@brief: auto publish weather report to twitter.
        Weather Infos fetched from www.weather.com.cn
        Twitter API from Python Twitter Tools(http://mike.verdone.ca/twitter/)

@usage:
    1. @itianqi set 城市名 | 城市全拼
                unset 城市名 | 城市全拼
        
        订阅相关城市的天气预报。每天0:00, 8:00, 12:00, 18:00发送。

    2. @itianqi 城市名 | 城市全拼
        获得最新实况天气信息(数据来自www.weather.com.cn)。如: @tianqi 北京 或 @itianqi beijing
        使用iPhone等终端可以看到天气图标
    
        今天是2011年1月8日,星期六,农历腊月初五
        北京今日多云转晴 1度至-8度
        08:40实况 -0.3度 西北风<3级 湿度22% (08:56:46)
        未来两天天气状况:
        明天 晴 -1度至-10度,
        后天 晴 0度至-8度 (08:56:46)

    3. @itianqi jnr 纪念日 [天数]
        根据当前日期，以及明年的纪念日获得纪念日信息。 如
        @itianqi jnr 2010-01-01 100
        第100天纪念日是2010-04-11, 您已经错过了272天!!
        @itianqi jnr 2010-01-01
        今天是第371天纪念日, 距离下一个纪念日还有358天, 请做好准备!!

    4. @itianqi 农历 | 日期
        获得当前日期信息，如：
        @itianqi 农历
        今天是2011年1月8日, 农历腊月初五 (08:19:25)

@to-do:
    *. lunar date look up
    1. world-wide time lookup
    2. calculation
    3. conversation (need to save every user's conversation)
    4. multiple reminder (weather_report subscription)

@history

1.4: 11/01/10 Fixed a bug caused by multiple city names with the same pinyin
                Create dictionary according to city names instead of pinyin to avoid ambiguity
                Also, store users' subscriptions in Chinese 
1.3: 11/01/10 Added hash tag for every weather report tweet, such as #tq #beijing
                This owes to @Imrunningsnail
1.2: 11/01/09 Added support for users to subscribe weather report for a certain city
1.1: 11/01/07 Added support to customized answers
              Added support to anniversary counting: get_jnr()
              Fixed a infinite loop bug due to self mention
1.0: 11/01/06 Added in_reply_status_id report for the mentions
0.9: 11/01/06 Fixed a bug that the image for "snow" is not put into emoji table
              Also created a emoji code table @ http://ibread.net/2011/01/emoji_code_table/
0.8: 11/01/06 Fixed a bug: Date is incorrect in the early morning (Due to error of data source)
                           ex. 2011/01/03 instead of 2011/01/04 in the morning
                           Fixed by getting system date and time of GMT+8
              Also added support to Lunardate to generate lunar date according to time zone (GMT+8)
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
from oauth_dance import oauth_dance
from api import Twitter, TwitterHTTPError
from oauth import OAuth, read_token_file
from datetime import datetime, tzinfo, timedelta
from lunardate import LunarDate
import sqlite3

base_path = sys.path[0] + os.sep
sub_file = base_path + 'subscribe.db'


def _py26OrGreater():
    import sys
    return sys.hexversion > 0x20600f0

if _py26OrGreater():
    import json
else:
    import simplejson as json

def only_ascii(string):
    '''
        Given a string, return if it contains only Ascii
    '''
    for c in string:
        if ord(c) > 255:
            return False
    
    return True
    
def lunar_today():
    '''
        Return today's lunar date
    '''
    day1=[u"初", u"十", u"廿", u"三"]
    day2=[u"十", u"一", u"二", u"三", u"四", u"五", u"六", u"七", u"八", u"九"]
    month=day2[:]
    month[1] = u"正"
    month.extend([u"十", u"冬", u"腊"])
    return u"%s月%s%s" % (month[LunarDate.today().month],
                       day1[LunarDate.today().day/10],
                       day2[LunarDate.today().day%10])

def get_weekday():
    '''
        Get today's weekday in Chinese
    '''
    weekdays = [u'一', u'二', u'三', u'四', u'五', u'六', u'日']
    nowdate =  datetime.now(tz=GMT8())
   
    return u'星期'+weekdays[nowdate.weekday()]

def get_date():
    '''
        Get today's date in Chinese
    '''
    nowdate =  datetime.now(tz=GMT8())
    return u"%d年%d月%d日" % (nowdate.year, nowdate.month, nowdate.day)

class GMT8(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=8)
    def tzname(self, dt):
        return "GMT +800"
    def dst(self, dt):
        return timedelta(0)

def format_date(date):
    '''
        Given a date like 2010-01-01 or 2010/01/01
        Return a valid datetime object if it is valid
        Otherwise return None
    '''
    if len(date.split('-')) == 3:
        try:
            date = date.split('-')
            [year, month, day] = map(lambda x: int(x.strip()), date)
            return datetime(year, month, day)
        except ValueError:
            print "Error foramting date from %s" % date
            return None
    elif len(date.split('/')) == 3:
        try:
            date = date.split('/')
            return datetime(date[0].strip(), date[1].strip(), date[2].strip())
        except ValueError:
            print "Error foramting date from %s" % date
            return None
    else:
        return None
    

def get_jnr(str):
    '''
        jnr 2010-01-12
        jnr 2010/01/12
            return today - 2010-01-12
            今天是第xxx天纪念日 :) 距离下个纪念日还有yyy天，请做好准备!!

        jnr 2010-01-12 100
            第100天纪念日是2010-xx-yy
    '''
    if not str.startswith('jnr '):
        msg = u"您输入的格式不正确，请使用jnr 2010-01-01 或 jnr 2010-01-01 100"
        return msg

    str = str.replace("jnr ", "")
    
    d = str.split()    

    anniver = format_date(d[0]) 
    if anniver == None:
        msg = u"您输入的格式不正确，请使用jnr 2010-01-01 或 jnr 2010-01-01 100"
        return msg

    nowdate = datetime.now()
    
    if len(d)==1:

        next_year = datetime(nowdate.year+1, anniver.month, anniver.day)
    
        elapsed = (nowdate - anniver).days
        left = (next_year - nowdate).days
        msg = u"今天是第%s天纪念日, 距离下一个纪念日还有%s天, 请做好准备!!" % (elapsed, left)
    elif len(d)==2:
        try:
            elapsed = timedelta(int(d[1]))
            next = anniver + elapsed            
            msg = u"第%d天纪念日是%s, " % (elapsed.days, next.strftime("%Y-%m-%d"))
            left_days = (next - nowdate).days
            if left_days < 0:
                msg += u"您已经错过了%s天!!" % (-left_days)
            else:
                msg += u"距离现在还有%s天!!" % (left_days)

        except ValueError:
            msg = u"您输入的格式不正确, 示例: jnr 2010-01-01 或 jnr 2010-01-01 100"
    else:
        msg = u"您输入的格式不正确，请使用jnr 2010-01-01 或 jnr 2010-01-01 100"

    return msg

def update_subscribe(move, id, city):
    '''
        move: add, remove
        id:   user id
        city: city
    '''
    
    conn = sqlite3.connect(sub_file)
    c = conn.cursor()
    #c.execute('''create table weather (id text PRIMARY KEY, city text)''')
    if move=="add":
        c.execute('select city from weather where id=?', (id,))
        results = c.fetchall()
        
        # if there is a record, then update it
        if len(results) > 0:
            c.execute('update weather set city=? where id=?', (city, id))
            print "user %s is already in, city %s" % (id, results[0][0])
        else: # insert it
            try:
                c.execute('insert into weather values (?, ?)', (id, city))
            except sqlite3.IntegrityError:
                print "user %s is already in, city is %s" % (id, results[0][0])
    elif move=="remove":
        c.execute('delete from weather where id=?', (id,))
        print "user %s is removed" % id
    
    conn.commit()
    c.close()
        

def get_weather(citycode="101010100", city_name=u'北京', debug=True):
    
    if debug:
        print "[Debug] Getting weather"

    #citycode = "101010100" # beijing
    fore_url = "http://m.weather.com.cn/data/%s.html" % (citycode) # forecast in 3 days(including today)
    rt_url = "http://www.weather.com.cn/data/sk/%s.html" % (citycode) # today's realtime

    try:
        forecast = urllib.urlopen(fore_url).read()
        realtime = urllib.urlopen(rt_url).read()
    except:
        print "Error retrieving weather information"
        return None, None

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

    # 晴天: \ue04a
    # 多云: \ue049
    # 阴天: \ue04d
    # 雨天: \ue04b
    # 小雪 (甜筒): \ue33a
    # 大雪, 阵雪, (雪人): \ue048

    # 0:晴天 1:多云 2:阴天 3~8: 雨 13:阵雪 14:小雪
    # 如果一天中天气没有变化，如多云转多云，后面这个会用99代替
    # 预览图标的话，可以用下面的网址 (Owe to @Paveo)
    # 只要把png文件的最后四个字母换成相应的unicode就可以了
    # http://obp.owind.com:801/emoji/emoji-E33A.png

    #print report
    emoji = {"0":u'\ue04a', "1":u'\ue049', "2":u'\ue04d', "3":u'\ue04b', \
             "4":u'\ue04b', "5":u'\ue04b', "6":u'\ue04b', "7":u'\ue04b', \
             "8":u'\ue04b', "13":u'\ue048', "14":u'\ue33a', "99":''}

    report_today = u"今天是%s,%s,农历%s \n%s今日%s%s%s %s\n%s实况 %s℃ %s%s级 湿度%s" % \
            (get_date(), get_weekday(), #forecast["date_y"], forecast["week"],  #forecast["date"], \
             lunar_today(), \
             city_name, \
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
    
    city_pinyin_hanzi = {} # beijing: 北京
    city_code_dict = {} # 北京:1000
    
    for line in f:
        hanzi, pinyin, code = map(lambda x: x.strip(), line.split())
        hanzi = hanzi.decode('utf8')
        city_code_dict [hanzi] = code
        #city_code_dict[pinyin] = code  

        if pinyin not in city_pinyin_hanzi.keys():
            city_pinyin_hanzi[pinyin] = hanzi
        else:
            city_pinyin_hanzi[pinyin] = city_pinyin_hanzi[pinyin] +  u' ' + hanzi

    return city_code_dict, city_pinyin_hanzi

def update(tweets="", debug=False):
    
    tw = get_twitter()
    
    points = [600, 1800]
    report_today, report_future = get_weather()
    if report_today is None:
        return

    # get dictionary city => code
    city_code_dict, city_pinyin_hanzi = get_code_dict()
    
    # convert {pinyin:hanzi} dict into {hanzi:pinyin} dict
    # because there might be multiple hanzi have the same pinyin
    # in {pinyin:hanzi} dict, it is represented as {pinyin: 'hanzi1 hanzi2 hani3'
    # when convert it back to {hanzi:pinyin}, we need to make sure if it is like this
    city_hanzi_pinyin = {}
    for k in city_pinyin_hanzi.keys():
        hanzi = city_pinyin_hanzi[k]
        if ' ' not in hanzi:
            city_hanzi_pinyin[hanzi] = k
        else:
            for h in hanzi.split():
                city_hanzi_pinyin[h] = k

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
            temp_report_today, temp_report_future = get_weather()
            if temp_report_today is not None:
                report_today, report_future = temp_report_today, temp_report_future

        dict_file = sys.path[0] + os.sep + "answers.txt"
        try:
            fdict = open(dict_file)
        except IOError as e:
            print "Error openning file %s" % dict_file
            print "Details", e
        
        answers = {}
        
        qa = fdict.readlines()

        for i in xrange(len(qa)/2):
            q = qa[2*i].decode('utf8').strip().lower()
            a = qa[2*i+1].decode('utf8')
            answers[q] = a

        # check mentions and reply back
        if True:
            try:
                mentions = tw.statuses.replies(count=count)
            except TwitterHTTPError:
                print "Error when getting all replies"
                print e
                print sys.exc_info()
                continue
            except:
                print "Error when getting all replies"
                print sys.exc_info()
                continue
            
            for m in mentions:
                # Already replied, do nothing                
                if m['id'] <= last_id:
                    if debug:
                        print "Already checked this mention: %s" % m['text']
                    break
                
                target = m['user']['screen_name']
                text = m['text']
                
                # ignore mention to myself
                if target == 'itianqi':
                    continue
                # ignore mentions which do not start with '@itianqi' 
                if not text.startswith('@itianqi'):
                    continue
                
                text = text.replace('@itianqi ', '')
                
                print "[Debug] %d %s says: %s" % (m['id'], target, text)
                
                # check if it contains command to set or unset subscription
                # set beijing | 北京
                # unset beijing | 北京
                if text.startswith('set') or text.startswith('unset'):
                    if text.startswith('set'):
                        command = "add"
                        text = text[3:].strip()
                    else:
                        command = "remove"
                        text = text[5:].strip()

                    try:
                        city = text.split()[0].strip()
                    except IndexError:
                        city = ""
                        # if command is set, you have to specify a city
                        if command == "add":
                            msg = u"您并未指定订阅城市，请使用@itianqi set beijing的形式指定城市"
                            try:
                                tw.statuses.update(status=u'@%s %s' % (target, msg), \
                                                   in_reply_to_status_id=u'%d' % m['id'])
                            except TwitterHTTPError as e:
                                print "    @%s %s" % (target, msg)
                                print "Details: ", e

                    city_name = city
                    
                    if only_ascii(city_name):
                        city_name = city_pinyin_hanzi[city]
                    if ' ' in city_name:
                        msg = u'您指定的城市拼音%s有歧义: %s, 请选择其中一个并使用set 城市中文名 的形式' % (city, city_name)
                        try:
                            tw.statuses.update(status=u'@%s %s' % (target, msg), \
                                               in_reply_to_status_id=u'%d' % m['id'])
                        except TwitterHTTPError as e:
                            print "Error!!!"
                            print "    @%s %s" % (target, msg)
                            print "Details: ", e
                        continue

                    original_city = city # backup for notifying the user what he/she input
                    # city => pinyin of city
                    if not only_ascii(city):
                        city = city_hanzi_pinyin[city]
                    
                    if command == "add":
                        if city_name in city_code_dict.keys():

                            update_subscribe(command, target, city_name)
                            
                            msg = u'操作已成功。您将会收到%s的天气预报提醒。' % city_name
                        
                        else:
                            msg = u"您指定的城市 %s 未找到，请修正后重试. :)" % origninal_city
                    else: # command == "remove"

                        conn = sqlite3.connect(sub_file)
                        c = conn.cursor()
                        c.execute('select city from weather where id=?', (target,))
                        results = c.fetchall()
                        c.close()

                        if len(results) == 0:
                            msg = u"很抱歉，您并未订阅天气预报。使用set 城市名|城市全拼 可订阅天气预报。"
                        else:
                            update_subscribe(command, target, city_name)

                            city_name = results[0][0]
                            msg = u'操作已成功。您订阅的%s的天气预报已取消，欢迎再次使用。' % city_name

                    try:
                        tw.statuses.update(status=u'@%s %s' % (target, msg), \
                                           in_reply_to_status_id=u'%d' % m['id'])
                    except TwitterHTTPError as e:
                        print "Error when replying with an answer:"
                        print "    @%s %s" % (target, msg)
                        print "Details: ", e

                    continue
                
                # 纪念日
                if text.startswith("jnr "):
                    if debug:
                        print "Entering jnr with %s" % m['text'].encode('utf8')
                    msg = get_jnr(text)
                    try:
                        tw.statuses.update(status=u'@%s %s' % (target, msg), \
                                           in_reply_to_status_id=u'%d' % m['id'])
                    except TwitterHTTPError as e:
                        print "Error when replying with an answer:"
                        print "    @%s %s" % (target, msg)
                        print "Details: ", e
                    continue


                if u"日期" in text or u"农历" in text:
                    now_time = curtime.strftime("%H:%M:%S")
                    msg = u"今天是%s, 农历%s" % (get_date(), lunar_today())
                    try:
                        tw.statuses.update(status=u'@%s %s (%s)' % (target, msg, now_time), \
                                           in_reply_to_status_id=u'%d' % m['id'])
                    except:
                        print "Error when posting replies"
                        print msg
                        print sys.exc_info()
                    continue
                
                # 智能问答
                if text in answers.keys() or text[:-1] in answers.keys():
                    msg = answers[text]
                    try:
                        tw.statuses.update(status=u'@%s %s' % (target, msg), \
                                           in_reply_to_status_id=u'%d' % m['id'])
                    except TwitterHTTPError as e:
                        print "Error when replying with an answer:"
                        print "    @%s %s" % (target, msg)
                        print "Details: ", e
                    continue
                    
                # this is used to avoid @itianqi reply a sentence which is not for asking weather
                # for example, I often use this to talk with somebody
                if len(text) > 10:
                    continue

                # determine if there is Chinese character 
                no_chinese = only_ascii(text)
                
                if no_chinese: #pinyin
                    text = text.lower()
                    citypinyin = text
                    if citypinyin not in city_pinyin_hanzi.keys():
                        msg = u'很抱歉，未找到您指定的城市全拼%s，请确认后重试或使用中文名' % citypinyin
                        try:
                            tw.statuses.update(status=u'@%s %s' % (target, msg), \
                                               in_reply_to_status_id=u'%d' % m['id'])
                        except TwitterHTTPError as e:
                            print "Error when replying with an answer:"
                            print "    @%s %s" % (target, msg)
                            print "Details: ", e
                        continue
                    
                    city_name = city_pinyin_hanzi[citypinyin]
                    if ' ' in city_name:
                        msg = u'您指定的城市拼音%s有歧义: %s, 请选择其中一个并使用set 城市中文名 的形式' % text
                        try:
                            tw.statuses.update(status=u'@%s %s' % (target, msg), \
                                               in_reply_to_status_id=u'%d' % m['id'])
                        except TwitterHTTPError as e:
                            print "Error when replying with an answer:"
                            print "    @%s %s" % (target, msg)
                            print "Details: ", e
                        continue
                else: # hanzi
                    city_name = text

                if city_name not in city_code_dict.keys():
                    msg = u'很抱歉，未找到您指定的城市名%s，请确认后重试。:)' % city_name
                    try:
                        tw.statuses.update(status=u'@%s %s' % (target, msg), \
                                           in_reply_to_status_id=u'%d' % m['id'])
                    except TwitterHTTPError as e:
                        print "Error when replying with an answer:"
                        print "    @%s %s" % (target, msg)
                        print "Details: ", e
                    continue
                else:
                    citycode = city_code_dict[city_name]

                    temp_report_today, temp_report_future = get_weather(citycode=citycode, city_name = city_name)
                    if temp_report_today is not None:
                        report_today, report_future = temp_report_today, temp_report_future

                    try:
                        now_time = curtime.strftime("%H:%M:%S")
                        msg = "Reply to %s @%s B %s" % (target, datetime.now(), text)
                        print msg.encode('utf8')
                        tw.statuses.update(status=u'@%s %s #tq #%s' % (target, report_future, citypinyin), \
                                           in_reply_to_status_id=u'%d' % m['id'])
                        tw.statuses.update(status=u'@%s %s #tq #%s' % (target, report_today, citypinyin), \
                                           in_reply_to_status_id=u'%d' % m['id'])
                    except:
                        print "Error when posting replies"
                        print msg
                        print sys.exc_info()
                    
                
                f.write("Reply to %s @%s" % (target, datetime.now()))
            
            last_id = mentions[0]['id']
            # update last_id
            try: 
                open(last_id_file, "w").write(str(last_id))
            except IOError:
                print "[Debug] Error updating last_id"
            
        if hourmin in points:
            # tweet weather report for beijing
            try:
                tw.statuses.update(status=report_future + "#tq #beijing")
                #tw.statuses.update(status=report_future.encode("utf-8"))
                tw.statuses.update(status=report_today + "#tq #beijing")
                print "Twitter %s" % "weather report"
            except Exception as e:
                print "Error when posting weather report"
                print report_today
                print report_future
                print sys.exc_info()
                print e
            
            # Get all ids in subscription and mention them weather report 
            # 1. Get all cities which are in subscription
            # 2. for each city, get the weather report 
            # 3. for each city, get the ids in subscription
            # 4. for each id, mention the weather report
            conn = sqlite3.connect(sub_file)

            c = conn.cursor()
            c.execute('''select distinct city from weather''')
            # sqlite3.IntegrityError
            # will be invoked when insert multiple record with the same primary key
            cities = c.fetchall()
            for city in cities:
                try:
                    citycode = city_code_dict[city[0]]
                except KeyError:
                    print "Error, the city %s in db is not in city list" % city[0].encode('utf8')
                    continue
                
                # city_name should be pinyin (all cities stored in db are pinyin)
                # but incase it is not, we do a conversion
                city_name = city[0]
                if only_ascii(city_name):
                    city_name = city_pinyin_hanzi[city_name]

                report_today, report_future = get_weather(citycode=citycode, city_name=city_name)
                
                c.execute('''select id from weather where city=?''', (city_name, ))
                ids = c.fetchall()
                for id in ids:
                    try:
                        print "pushing report: @%s %s" % (id[0], city_name)
                        tw.statuses.update(status=u'@%s %s #tq #%s' % (id[0], report_today, city_name))
                        tw.statuses.update(status=u'@%s %s #tq #%s' % (id[0], report_future, city_name))
                    except Exception as e:
                        print "Error when pushing report to %s" % id
                        print repr(e)

            c.close()
        
            
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



if __name__ == "__main__":
    if len(sys.argv)==1:
        update()
    else:
        update(sys.argv[1])
