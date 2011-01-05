#coding: UTF-8
#!/usr/bin/python

import urllib, os, sys, time
import os.path
from oauth_dance import oauth_dance
from api import Twitter, TwitterError
from oauth import OAuth, write_token_file, read_token_file
import random

def main():
    CONSUMER_KEY = "NXdiUFv7ZqhO5Ojr8GocA"
    CONSUMER_SECRET = "CMRgb7BHpHLlcZ0NqHF06pWbFtv1zPqV98KTaFxV2YQ"
    oauth_filename = os.environ.get('HOME', '') + os.sep + '.my_twitter_oauth'
    print oauth_filename
    if not os.path.exists(oauth_filename):
        oauth_dance("ibread", CONSUMER_KEY, CONSUMER_SECRET, oauth_filename)

    oauth_token, oauth_token_secret = read_token_file(oauth_filename)

    print oauth_token, oauth_token_secret

    tw = Twitter(
        auth=OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET),
        secure=True,
        api_version='1',
        domain='api.twitter.com')
    
    #x = tw.statuses.friends_timeline(count=10)
    #for i in x:
    #    pass
    #    print i['user']['screen_name'], i['text']

    tw.statuses.update(status=u'好困啊')
    
    #tw.statues.update(status=u"Test".encode('utf8', 'replace'))


if __name__ == "__main__":
    main()
