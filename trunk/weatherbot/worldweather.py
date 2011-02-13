#!/usr/bin/env python
# coding: UTF-8
# @file: worldweather.py
# @date: Jan. 29, 2011
# @brief: Return current weather report and forecast according to the city
#         Use Google Weather API (http://www.google.com/api?weather)
# @author: breaddawson@gmail.com

import urllib2
from xml.dom import minidom
import sys

def FtoC(f):
    '''
        Return Celsius degree by given Fahrenheit
        C = (F-32)/1.8
    '''
    try:
        f = int(f)
        c = (f-32)/1.8
        return int(c)
    except Exception as e:
        print e
        return ''
    
def CtoF(c):
    '''
        Return Fahrenheit degree by given Celsius 
        F = 32 + C*1.8
    '''
    try:
        c = int(c)
        f = c*1.8 + 32
        return int(f)
    except Exception as e:
        print e
        return ''

def getElementValue(xmldata, l):
    '''
        Get element value from xmldata
        I use this function because xmldata returned by Google is well formated
        and in every single element, data is always in the attribute named 'data'
    '''
    #if type(l).__name__ != 'list':
    #    return None
    #if len(l) < 1:
    #    return None

    try:
        info = xmldata.getElementsByTagName(l)[0]
        return info.attributes['data'].value
    except IndexError:
        print "[Error] no %s information in xmldata" % l
        return ''
        

def worldweather(city = u'Beijing', debug=False):
    '''
        Return current report and forecase of Given data

        Format:
            Beijing, China
            Current Time: 2011-01-29 19:02:46
            Clear
            Wind: NW at 13 mph
            Humidity: 28%

            Sun: Shower 1°C | -9°C
            Mon: Cloudy 6°C | -6°C
    '''
    API = 'http://www.google.com/ig/api?weather='
    city = '+'.join(city.split())
    query = urllib2.unquote(API.encode('utf8') + city.encode('utf8'))
    if debug:
        print query

    try:
        u = urllib2.urlopen(query)
        encoding = u.headers['Content-type'].split('charset=')[1]
        s = u.read().decode(encoding).encode('utf8')
        if debug:
            print s
        results = minidom.parseString(s)
    except Exception as e:
        print e
        return None

    # Get basic information of the city and current time
    try:
        basic =  results.getElementsByTagName('forecast_information')[0]
    except IndexError:
        if debug:
            print "[Error] No forecast_information node"
        return None

    # u'2011-01-29 19:02:46 +0000'
    current_date = getElementValue(basic, 'current_date_time')
    if current_date == '':
        print "[Error] No current_date_time info"
    # u'2011-01-29 19:02:46'
    current_date = current_date[:current_date.find('+')].strip()

    city_name = getElementValue(basic, 'city')

    # Get current condition 
    try:
        current =  results.getElementsByTagName('current_conditions')[0]
    except IndexError:
        if debug:
            print "[Error] No current_conditions node"
        return None

    #<current_conditions>
    #    <condition data="Partly Cloudy"/>
    #    <temp_f data="54"/>
    #    <temp_c data="12"/>
    #    <humidity data="Humidity: 77%"/>
    #    <icon data="/ig/images/weather/partly_cloudy.gif"/>
    #    <wind_condition data="Wind: SE at 7 mph"/>
    #</current_conditions>
    current_cond = getElementValue(current, 'condition')
    current_temp = getElementValue(current, 'temp_c')
    current_humi = getElementValue(current, 'humidity')
    current_wind = getElementValue(current, 'wind_condition')

    
    # Beijing, China
    # Current Time: 2011-01-29 19:02:46
    # Clear 1°C
    # Wind: NW at 13 mph
    # Humidity: 28%
    today =  u"%s \nCurrently %s %s°C \n%s\n%s\n(%s)" % (city_name, current_cond, current_temp, current_wind, current_humi, current_date)

    
    # Get Forecast of next two days
    forecasts =  results.getElementsByTagName('forecast_conditions')
    future = ""
    if len(forecasts) < 2:
        print '[Error] no forecast'
    else:
        for i in xrange(2):
            #<forecast_conditions>
            #    <day_of_week data="Sat"/>
            #    <low data="49"/>
            #    <high data="60"/>
            #    <icon data="/ig/images/weather/cloudy.gif"/>
            #    <condition data="Cloudy"/>
            #</forecast_conditions>
            forecast = forecasts[i] 
            dow = getElementValue(forecast, 'day_of_week')
            condition = getElementValue(forecast, 'condition')
            temp_low = getElementValue(forecast, 'low')
            temp_high = getElementValue(forecast, 'high')
            # Sun: Shower 1°C | -9°C
            # Mon: Cloudy 6°C | -6°C
            future += u'%s: %s %s°C | %s°C\n' % (dow, condition, FtoC(temp_high), FtoC(temp_low))

    future += "[via Google]"
    return (today, future)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print worldweather(u'香港', True)
    else:
        print worldweather(' '.join(sys.argv[1:]), True)
    

#<weather mobile_row="0" mobile_zipped="1" module_id="0" row="0" section="0" tab_id="0">
#    <forecast_information>
#        <city data="Mountain View, CA"/>
#        <postal_code data="Mountain View"/>
#        <latitude_e6 data=""/><longitude_e6 data=""/>
#        <forecast_date data="2011-01-29"/>
#        <current_date_time data="2011-01-29 19:02:46 +0000"/>
#        <unit_system data="US"/>
#    </forecast_information>
#    <current_conditions>
#        <condition data="Partly Cloudy"/>
#        <temp_f data="54"/>
#        <temp_c data="12"/>
#        <humidity data="Humidity: 77%"/>
#        <icon data="/ig/images/weather/partly_cloudy.gif"/>
#        <wind_condition data="Wind: SE at 7 mph"/>
#    </current_conditions>
#    <forecast_conditions>
#        <day_of_week data="Sat"/>
#        <low data="49"/>
#        <high data="60"/>
#        <icon data="/ig/images/weather/cloudy.gif"/>
#        <condition data="Cloudy"/>
#    </forecast_conditions>
#    <forecast_conditions>
#        <day_of_week data="Sun"/>
#        <low data="42"/>
#        <high data="56"/>
#        <icon data="/ig/images/weather/rain.gif"/>
#        <condition data="Showers"/>
#    </forecast_conditions>
#    <forecast_conditions>
#        <day_of_week data="Mon"/>
#        <low data="43"/>
#        <high data="58"/>
#        <icon data="/ig/images/weather/sunny.gif"/>
#        <condition data="Sunny"/>
#    </forecast_conditions>
#    <forecast_conditions>
#        <day_of_week data="Tue"/>
#        <low data="37"/>
#        <high data="58"/>
#        <icon data="/ig/images/weather/sunny.gif"/>
#        <condition data="Sunny"/>
#    </forecast_conditions>
#</weather>'
