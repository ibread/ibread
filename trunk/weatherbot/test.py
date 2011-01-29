#!/usr/bin/python
#coding: utf8

from datetime import datetime
from datetime import tzinfo, timedelta
import json
import sys, os
from pinyin import *
from lunardate import LunarDate
import sqlite3

cur_path = sys.path[0] + os.sep
conn = sqlite3.connect(cur_path + "subscribe.db")

c = conn.cursor()
#c.execute('''create table weather(id text, city text)''')
# sqlite3.IntegrityError
# will be invoked when insert multiple record with the same primary key

#c.execute('''insert into weather values ('bread', '123')''')
#c.execute('''insert into weather values ('a1', '123')''')
#c.execute('''insert into weather values ('a2', '123')''')
#c.execute('''insert into weather values ('a3', '123')''')

#c.execute('''insert into weather values (?, ?)''', ('ibread', u'北京'))
#c.execute('''insert into weather values (?, ?)''', ('amy_guo', u'北京'))
#c.execute('''insert into weather values (?, ?)''',  ('Imrunningsnail', u'杭州'))
#
#c.execute('''update weather set city=? where id=?''', (u'北京', 'ibread'))
#c.execute('''update weather set city=? where id=?''', (u'北京', 'amy_guo'))
#c.execute('''update weather set city=? where id=?''', (u'杭州', 'Imrunningsnail'))

c.execute('select * from weather')
results = c.fetchall()
for r in results:
    print r[0].encode('utf8'), r[1].encode('utf8')

conn.commit()
c.close()
sys.exit(1)


def only_ascii(string):
    '''
        Given a string, return if it contains only Ascii
    '''
    for c in string:
        if ord(c) > 255:
            return False
    
    return True

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


def post_realtime(text):
    '''
        Post realtime weather and weather report to user
        @parms:
            text: the text provid
    '''

    # this is used to avoid @itianqi reply a sentence which is not for asking weather
    # for example, I often use this to talk with somebody
    if len(text) > 10:
        return

    cd = CityDict()

    try:
        pinyin, hanzi, code = cd.get_city(text)
        print pinyin, hanzi, code
    except ValueError as e:
        print e.args


post_realtime('beijing')
post_realtime('haha')
post_realtime('yiwu')
post_realtime(u'哈哈')

sys.exit(1)

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
        raise ValueError, "%s Not as 1985-09-06 or 1985/09/06" % date

    if len(split_date) != 3:
        raise ValueError, "%s Not as 1985-09-06 or 1985/09/06" % date
    
    year = int(split_date[0])
    month = int(split_date[1])
    day = int(split_date[2])

    if year < 1900 or year > 2049:
        raise ValueError, "Year should in [1900, 2049]"

    date = datetime(year, month, day)

    date = LunarDate.fromSolarDate(year, month, day)
        
    day1=[u"初", u"十", u"廿", u"三"]
    day2=[u"十", u"一", u"二", u"三", u"四", u"五", u"六", u"七", u"八", u"九"]
    month=day2[:]
    month[1] = u"正"
    month.extend([u"十", u"冬", u"腊"])
    return u"%s年%s月%s%s" % (date.year, month[date.month], day1[date.day/10], day2[date.day%10])
    # check format of date

if len(sys.argv) > 1:
    print lunar_date(sys.argv[1])
sys.exit(1)





class GMT(tzinfo):
    bread = 8
    def __init__(self, bread):
        self.bread = bread
    def utcoffset(self, dt):
        return timedelta(hours=self.bread)
    def tzname(self, dt):
        return "GMT +800"
    def dst(self, dt):
        return timedelta(0)

print datetime.now(tz=GMT(8))
sys.exit(1)

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
    print str
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

        next_year = datetime(anniver.year+1, anniver.month, anniver.day)
    
        elapsed = (nowdate - anniver).days
        left = (next_year - nowdate).days
        msg = u"今天是第%s天纪念日, 距离下一个纪念日还有%s天, 请做好准备!!" % (elapsed, left)
    elif len(d)==2:
        try:
            elapsed = timedelta(int(d[1]))
            next = anniver + elapsed            
            msg = u"第%d天纪念日是%s, 请务必做好准备!!" % (elapsed.days, next.strftime("%Y-%m-%d"))
        except ValueError:
            msg = u"您输入的格式不正确, 示例: jnr 2010-01-01 或 jnr 2010-01-01 100"
    else:
        msg = u"您输入的格式不正确，请使用jnr 2010-01-01 或 jnr 2010-01-01 100"

    return msg


print get_jnr("2011-01-07")
print get_jnr("jnr 2011-01-07")
print get_jnr("jnr 2011-01-07 10")
sys.exit(1)




data = json.loads(open("city.json").read())

city_url = {}

for d in data:
    #print d['key'].encode('utf8'), d['url'].encode('utf8')
    if d['key'] not in city_url.keys() or city_url[d['key']] is None:
        city_url[d['key']] = d['url'] 
    #print d['key'].encode('utf8'), repr(d['key'])

print repr(u'上海')
print u'北京' in city_url.keys()
print city_url[u'上海']

for k in city_url.keys():
    pass
    #print k,

for k in city_url.keys():
    print k.encode('utf8'), hanzi2pinyin(k),  
    if city_url[k] is None:
        print "None"
    else:
        print city_url[k].encode('utf8')
