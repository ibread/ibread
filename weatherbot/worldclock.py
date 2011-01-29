#!/usr/bin/env python
# coding: utf8

import urllib2
import re
import sys

def worldclock(city = u"北京", debug=False):
    '''
        Given a city, return the current time of it
    '''

    city = '+'.join(city.split())

    query = 'http://www.google.com/search?q=time+'.encode('utf8') + city.encode('utf8')
    try:
        query = urllib2.unquote(query)
    except urllib2.HTTPError:
        return None

    if debug:
        print "query is ", query
    pattern = '<div class="s rbt">.*?</div>'

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = opener.open(query)
    content = response.read()
    results = re.findall(pattern, content)
    # ['<div class="s rbt"><table cellpadding=0 class=obcontainer><tr><td valign=top><h3 class=r></h3><tr><td valign=top width=100%><div><table cellspacing=0><tr><td style="font-size:medium"><b>10:16am</b> Sunday (CST) - <b>Time</b> in <b>Beijing, China</b></table></div>']
    if len(results) > 0:
        # ['10:16am', 'Time', 'Beijing, China']
        t = re.findall(r'<b>(.*?)</b>', results[0])
        # ['</b> Sunday (CST) - <b>', '</b> in <b>']
        w = re.findall(r'</b>(.*?)<b>', results[0])
        if debug:
            print t, w
        if len(t) > 2 and len(w) > 0:
            return "%s %s, %s" % (t[0].decode('utf8'), w[0].strip('- ').decode('utf8'), t[2].decode('utf8'))

    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s CITYNAME" % sys.argv[0]
        sys.exit(1)

    print worldclock(u'北京', debug=True)
