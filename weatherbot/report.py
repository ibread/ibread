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
<<<<<<< .mine
    经过老婆提醒，应该注意下定位，准备尽快加下面几个功能    

    1. 穿衣指数等详细信息
    2. 农历禁忌等
    3. 世界时钟

=======

    * Improve lunar date lookup
    2. calculation
    3. conversation (need to save every user's conversation)

@history

2.0: 11/01/27 Added wordclock support
1.9: 11/01/17 Adde exception handling to get_weather(), no more crash due to this any more!
1.8: 11/01/15 Added help information
              Fixed a bug that only mention with Chinese city name will reply with report
1.7: 11/01/15 Fixed a bug thath metions forgets reply_id
              Added the feature back that reply weather info to user even they do not use tq command 
1.6: 11/01/10 Rewrite the main logic: intelligent answer is not the default behavior
                realtime weather report need "tq" command
1.5: 11/01/10 Added lunar date lookup (need to be improved later)
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
from twitter.oauth_dance import oauth_dance
from twitter.api import Twitter, TwitterHTTPError
from twitter.oauth import OAuth, read_token_file
from datetime import datetime, tzinfo, timedelta
from lunardate import LunarDate
import sqlite3
from worldclock import worldclock
from worldweather import worldweather

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
        Given a unicode string, return if it contains only Ascii
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
                       day1[(LunarDate.today().day-1)/10],
                       day2[LunarDate.today().day%10])

def lunar_date(date):
    '''
        Return lunar date accodring to given date
        Its format should be 1985-09-06 or 1985/09/06
        
        raise Value error if date is not correct
    '''
    
    if '-' in date:
        split_date = date.split('-')
    elif '/' in date:
        split_date = date.split('/')
    else:
        raise ValueError("%s Not as 1985-09-06 or 1985/09/06" % date)

    if len(split_date) != 3:
        raise ValueError("%s Not as 1985-09-06 or 1985/09/06" % date)
    
    year = int(split_date[0])
    month = int(split_date[1])
    day = int(split_date[2])

    if year < 1900 or year > 2049:
        raise ValueError("Year should in [1900, 2049]")

    date = datetime(year, month, day)

    date = LunarDate.fromSolarDate(year, month, day)
        
    day1=[u"初", u"十", u"廿", u"三"]
    day2=[u"十", u"一", u"二", u"三", u"四", u"五", u"六", u"七", u"八", u"九"]
    month=day2[:]
    month[1] = u"正"
    month.extend([u"十", u"冬", u"腊"])
    return u"%s年%s月%s%s" % (date.year, month[date.month], day1[date.day/10], day2[date.day%10])

def get_weekday():
    '''
        Get today's weekday in Chinese
    '''
    weekdays = [u'一', u'二', u'三', u'四', u'五', u'六', u'日']
    nowdate =  datetime.now(tz=GMT8())
   
    return u'周'+weekdays[nowdate.weekday()]

def get_date():
    '''
        Get today's date in Chinese
    '''
    nowdate =  datetime.now(tz=GMT8())
    #return u"%d年%d月%d日" % (nowdate.year, nowdate.month, nowdate.day)
    return u"%d月%d日" % (nowdate.month, nowdate.day)

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
            print ("Error foramting date from %s" % date).encode('utf8')   
            return None
    elif len(date.split('/')) == 3:
        try:
            date = date.split('/')
            return datetime(date[0].strip(), date[1].strip(), date[2].strip())
        except ValueError:
            print ("Error foramting date from %s" % date).encode('utf8')
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
        try:
            c.execute('insert into weather values (?, ?)', (id, city))
            print (u"user %s, city %s added" % (id, city)).encode('utf8')
        except sqlite3.IntegrityError:
            print ("error when inserting user %s, city %s" % (id, results[0][0])).encode('utf8')
    elif move=="remove":
        c.execute('delete from weather where id=? and city=?', (id, city))
        print ("user %s city %s is removed" % (id, city)).encode('utf8')
    
    conn.commit()
    c.close()
        

def get_weather(citycode="101010100", city_name=u'北京', debug=True):
    '''
        Return weather report information with given city
    '''
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
    # 阴天: \ue04d  => \uE03B (Suggested by Amy)
    # 雨天: \ue04b
    # 小雪 (甜筒): \ue33a
    # 小到中雪 : \ue33a 26
    # 中雪: \ue43F 15
    # 大雪, 阵雪, (雪人): \ue048

    # 0:晴天 1:多云 2:阴天 3~8: 雨 13:阵雪 14:小雪
    # 如果一天中天气没有变化，如多云转多云，后面这个会用99代替
    # 预览图标的话，可以用下面的网址 (Owe to @Paveo)
    # 只要把png文件的最后四个字母换成相应的unicode就可以了
    # http://obp.owind.com:801/emoji/emoji-E33A.png

    #print report
    emoji = {"0":u'\ue04a', "1":u'\ue049', "2":u'\ue03b', "3":u'\ue04b', \
             "4":u'\ue04b', "5":u'\ue04b', "6":u'\ue04b', "7":u'\ue04b', \
             "8":u'\ue04b', "13":u'\ue048', "14":u'\ue33a', "15":u'\ue43F', \
             "26":u'\ue33a', "99":''}

    try:
        # u'\xb0' is °
        report_today = u"今天是%s,%s,农历%s %s今日%s%s%s %s\n%s实况 %s°C %s%s级 湿度%s" % \
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

        report_today = report_today.replace(u"\u2103", u"°C")
        report_today = report_today.replace(u"~", u"至")
        report_future = report_future.replace(u"\u2103", u"°C")
        report_future = report_future.replace(u"~", u"至")
    
    except KeyError as e:
        f.write(u"%s\n" % e)
        return None, None

    f.close()

    if debug:
        print "[Debug] Done getting weather"
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

def post_msg(tw, msg, reply_id=0):

    if reply_id != 0:
        try:
            tw.statuses.update(status=msg, in_reply_to_status_id=u'%d' % reply_id)
        except TwitterHTTPError as e:
            print ("[Error] %s" % msg).encode('utf8')
            print "Details: ", e
            return 1
    else:
        try:
            tw.statuses.update(status=msg)
        except TwitterHTTPError as e:
            print "[Error] %s" % msg.encode('utf8')
            print "Details: ", e
            return 1

    return 0
        

class CityDict():
    def __init__(self):
        dict_file = sys.path[0] + os.sep + "city_code.dat" 
        try:
            f = open(dict_file)
        except IOError:
            raise IOError ("Error openning %s" % dict_file)
        
        self.pinyin_hanzi = {} # beijing: 北京
        self.code_dict = {} # 北京:1000
        self.hanzi_pinyin = {} # 北京:beijing

        for line in f:
            hanzi, pinyin, code = map(lambda x: x.strip(), line.split())
            hanzi = hanzi.decode('utf8')
            self.code_dict[hanzi] = code
            self.hanzi_pinyin[hanzi] = pinyin
            #city_code_dict[pinyin] = code  

            if pinyin not in self.pinyin_hanzi.keys():
                self.pinyin_hanzi[pinyin] = hanzi
            else:
                self.pinyin_hanzi[pinyin] = self.pinyin_hanzi[pinyin] +  u' ' + hanzi
        
    def get_city(self, city):
        '''
            With given city (pinyin or hanzi)
            if it is valid (included in cities list)
                return city_pinyin, city_hanzi, city_code
            else rasie ValueError exception, and return error message
        '''
       
        city = city.strip().lower()
        if only_ascii(city):
            city_pinyin = city
            if city not in self.pinyin_hanzi.keys():
                raise ValueError(u"很抱歉，并未找到您指定的城市全拼 %s，请确认后重试或使用中文名称。" % city)

            city_hanzi = self.pinyin_hanzi[city]
            if ' ' in city_hanzi:
                raise ValueError(u"您提供的城市拼音%s对应多个城市%s，请选择后重试。" % (city, city_hanzi))
        else:
            city_hanzi = city
            if city not in self.hanzi_pinyin.keys():
                raise ValueError(u"很抱歉，未找到您指定的城市 %s，请确认后重试。" % city)
            
            city_pinyin = self.hanzi_pinyin[city]

        city_code = self.code_dict[city_hanzi]
        
        return city_pinyin, city_hanzi, city_code 


def post_realtime(text, tw, target, mid, cd):
    '''
        Post realtime weather and weather report to user
        @parms:
            text: the text provided by users
            tw: twitter object
            target: user's screen name
            mid: id of user's tweet
            cd: city dictionary object
    '''

    try:
        pinyin, hanzi, code = cd.get_city(text)
        print pinyin.encode('utf8'), hanzi.encode('utf8'), code.encode('utf8')
    except ValueError as e: # Error occurs
        # msg = u"@%s %s" % (target, e.args[0])
        raise ValueError(e.args[0])

    report_today, report_future = get_weather(citycode=code, city_name = hanzi)
    if report_today is None:
        msg = u"很抱歉。获取%s天气信息失败，请稍后重试。"
        return post_msg(tw, msg, mid)

    curtime = datetime.now(tz=GMT8())
    now_time = curtime.strftime("%H:%M:%S")
    msg = "Reply to %s @%s id %s B %s" % (target, datetime.now(), mid, text)
    print msg.encode('utf8')
    post_msg(tw, u'@%s %s #tq #%s' % (target, report_future, pinyin), mid)
    post_msg(tw, u'@%s %s #tq #%s' % (target, report_today, pinyin), mid)

def update(tweets="", debug=True):
    
    tw = get_twitter()
    
    points = [810, 1800]
    report_today, report_future = get_weather()
    if report_today is None:
        return

    cd = CityDict()

    # set up log file
    logpath = sys.path[0] + os.sep
    f = open(logpath+"weather.log", "a+")

    last_id_file = logpath+"last_id.dat"
    try:
        last_id = int(open(last_id_file).readline().strip())
    except (IOError, ValueError):
        last_id = 0L
        
    count = 10 # check latest 10 mentions every time
    period = 0.5*60 # check mention every 0.5 minute
    
    while True:
        curtime = datetime.now(tz=GMT8())
        hour, min, sec = curtime.hour, curtime.minute, curtime.second
        
        hourmin = hour*100+min

        if debug:
            print "[Debug] Curtime: %s"  % curtime
            print "[Debug] hourmin: %s"  % hourmin
        
        # update the report at certain time points
        if hourmin % 100 == 0:
            temp_report_today, temp_report_future = get_weather()
            if temp_report_today is not None:
                report_today, report_future = temp_report_today, temp_report_future

        dict_file = sys.path[0] + os.sep + "answers.txt"
        try:
            fdict = open(dict_file)
        except IOError as e:
            print "Error openning file %s" % dict_file
            print "Details", e
        
        # build answers dictionary
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
            except Exception as e:
                print "Error when getting all replies"
                #print e
                #print sys.exc_info()
                time.sleep(period)
                continue

            for m in mentions:
                # Already replied, do nothing                
                if m['id'] <= last_id:
                    #if debug:
                        #print "Already checked this mention: %s" % m['text'].encode('utf8')
                    break
                
                target = m['user']['screen_name']
                text = m['text']
                
                # ignore mention to myself
                if target == 'itianqi':
                    continue
                # ignore mentions which do not start with '@itianqi' 
                if not text.startswith('@itianqi'):
                    continue
                
                text = text.replace('@itianqi ', '').strip()
                print (u"[Debug] %d %s says: %s" % (m['id'], target, text)).encode('utf8')
                
                # check if the text is only the city
                # if there is no ValueError, which means it is a city
                # then return the weather report information for that city
                # else to continue to check other rules
                city = text.strip()
                try:
                    cd.get_city(city)
                    print (u"reply with city %s " % city).encode('utf8')
                    post_realtime(city, tw, target, m['id'], cd)
                    continue
                except ValueError as e:
                    if u"对应多个城市" in e[0]:
                        post_msg(tw, u'@%s %s' % (target, e[0]), m['id'])
                        continue
                    pass

                # check to see if it is a world city
                # we do this by checking return value from worldweather
                try:
                    ww = worldweather(city)# , True)
                    #print ww
                except Exception as e:
                    print e
                if ww is not None:
                    ww_today = u'@%s %s' % (target, ww[0])
                    ww_future = u'@%s %s' % (target, ww[1])
                    post_msg(tw, ww_future, m['id'])
                    post_msg(tw, ww_today, m['id'])
                    continue

                if text.startswith(u'help') or text.startswith(u'帮助'):
                    msg = u"@itianqi 直接输入城市获得实况天气信息。set 城市订阅天气预报，unset取消订阅。支持订阅多个城市以及城市拼音。nl 公历日期查询万年历。详情请查看http://goo.gl/Ffg47" 
                # check if user want to get status of subscription
                elif text.startswith('get'):
                    conn = sqlite3.connect(sub_file)
                    c = conn.cursor()
                    c.execute('select city from weather where id=?', (target,))
                    results = c.fetchall()
                    c.close()

                    if len(results)==0:
                        msg = u"您并未订阅任何城市的天气预报。请使用@itianqi set 城市中文或拼音 订阅"
                    
                    cities = ""
                    for c in results:
                        cities += (c[0] + " ")
                    
                    msg = u"您订阅了如下城市的天气预报: %s" % cities
                    
                # check if it contains command to set or unset subscription
                # set beijing | 北京
                # unset beijing | 北京
                elif text.startswith('set') or text.startswith('unset'):
                    if text.startswith('set'):
                        command = "add"
                        text = text[3:].strip()
                    elif text.startswith('unset'):
                        command = "remove"
                        text = text[5:].strip()

                    try:
                        city = text.split()[0].strip()
                    except IndexError:
                        msg = u"您并未指定订阅城市，请使用@itianqi set beijing的形式指定城市"
                        post_msg(tw, u'@%s %s' % (target, msg), m['id'])
                        continue

                    print "city=", city.encode('utf8')

                    try:
                        city_pinyin, city_hanzi, city_code = cd.get_city(city)
                    except ValueError as e:
                        post_msg(tw, u"@%s %s" % (target, e[0]), m['id'])
                        continue
                    
                    original_city = city # backup for notifying the user what he/she input
                    
                    if command == "add":
                            update_subscribe(command, target, city_hanzi)
                            msg = u'操作已成功。您将会收到%s的天气预报提醒。' % city_hanzi
                    else: # command == "remove"

                        conn = sqlite3.connect(sub_file)
                        c = conn.cursor()
                        c.execute('select city from weather where id=? and city=?', (target, city_hanzi))
                        results = c.fetchall()
                        c.close()

                        if len(results) == 0:
                            msg = u"很抱歉，您并未订阅%s的天气预报。使用set 城市名|城市全拼 可订阅天气预报。" % city_hanzi
                        else:
                            update_subscribe(command, target, city_hanzi)
                            city_name = results[0][0]
                            msg = u'操作已成功。您订阅的%s的天气预报已取消，欢迎再次使用。' % city_name

                # 纪念日
                elif text.startswith("jnr "):
                    if debug:
                        print "Entering jnr with %s" % m['text'].encode('utf8')
                    msg = get_jnr(text)

                elif text==u"日期" or text==u"农历" or text==u"nl":
                    now_time = curtime.strftime("%H:%M:%S")
                    msg = u"今天是%s, 农历%s" % (get_date(), lunar_today())

                # Solar date => Lunar date
                elif text.startswith("nl") and len(text.split()) > 1:
                    date = text.split()[1]
                    try:
                        lunar = lunar_date(date)
                        msg = u"%s的农历日期是%s" % (date, lunar)
                    except ValueError, e:
                        print e
                        msg = u"您所提供的日期%s格式不正确, 请参照1985-09-06或1985/09/06"

                # World Clock
                elif text.startswith("time ") and len(text.split()) > 1:
                    city = text.replace('time ', '').strip()
                    t = worldclock(city)
                    if t is None:
                        msg = u"很抱歉，并未找到您提供的城市 %s 的时间信息。请确认后重试 :)" % city
                    else:
                        msg = u"当前时间: %s" % (t)
                    
                # Realtime weather report
                # we could deal with both Chinese city and world cities
                elif text.startswith('tq'):
                    city = text.replace('tq', '').strip()
                    if len(city) == 0:
                        city = 'beijing'
                    try:
                        post_realtime(city, tw, target, m['id'], cd)
                    except ValueError as e:
                        if u'对应多个城市' in e.args[0]:
                            post_msg(tw, e.args[0], m['id'])
                        else: # cannot find the city, try worldcities
                            error_msg = e.args[0]
                            try:
                                ww = worldweather(city)
                            except Exception as e:
                                print e
                            if ww  is not None: # found weather info for world cities
                                ww_today = u'@%s %s' % (target, ww[0])
                                ww_future = u'@%s %s' % (target, ww[1])
                                post_msg(tw, ww_future, m['id'])
                                post_msg(tw, ww_today, m['id'])
                            else:
                                post_msg(tw, error_msg, e.args[0])
                    continue
                
                # Intelligent answers
                elif text in answers.keys():
                    msg = answers[text]
                elif text[:-1] in answers.keys():
                    msg = answers[text[:-1]]
                else:
                    msg = u'感谢您的关注，我会继续努力的! 使用@itianqi help可以查看基本功能 :)'
                    
                if target == "amy_guo":
                    words = [u"谁最好看", u"谁最漂亮", u"谁最美"]
                    results = map(lambda x:x in text, words)
                    haokan = reduce(lambda x,y: x or y)
                    if haokan:
                        msg = u'当然是你啦。:) '
                    
                print ("@%s %s" % (target, msg)).encode('utf8')
                post_msg(tw, u'@%s %s' % (target, msg), m['id'])
                
                f.write("Reply to %s @%s" % (target, datetime.now()))
            
            last_id = mentions[0]['id']
            # update last_id
            try: 
                open(last_id_file, "w").write(str(last_id))
            except IOError:
                print "[Debug] Error updating last_id"
            
        if hourmin in points:
            # tweet weather report for beijing
            post_msg(tw, report_future + "#tq #beijing")
            post_msg(tw, report_today + "#tq #beijing")
            print "Twitter %s" % "weather report"
            
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
                    city_pinyin, city_hanzi, city_code = cd.get_city(city[0])
                except Exception:
                    print u"[Error] city %s in db is invalid" % city[0]
                    continue

                report_today, report_future = get_weather(citycode=city_code, city_name=city_hanzi)
                if report_today is None:
                    try:
                        print u"[Error] Can not retrieve weather report for %s" % city_hanzi
                    except UnicodeEncodeError as e:
                        print repr(city_hanzi)

                    continue
                
                c.execute('''select id from weather where city=?''', (city_hanzi, ))
                ids = c.fetchall()
                for id in ids:
                    print ("pushing report: @%s %s" % (id[0], city_hanzi)).encode('utf8')
                    post_msg(tw, u'@%s %s #tq #%s' % (id[0], report_future, city_pinyin))
                    post_msg(tw, u'@%s %s #tq #%s' % (id[0], report_today, city_pinyin))

            c.close()
        
            
        time.sleep(period)
                
    f.close()
    

if __name__ == "__main__":
    #cd = CityDict()
    #print cd.get_city('Nanjing')
    #sys.exit(1)
    if len(sys.argv)==1:
        update()
    else:
        tw = get_twitter()
        post_msg(tw, u'8°C | 6°C')
