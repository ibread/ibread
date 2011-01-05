#!/usr/bin/python

from datetime import datetime
from datetime import tzinfo, timedelta

class GMT8(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=8)
    def tzname(self, dt):
        return "GMT +800"
    def dst(self, dt):
        return timedelta(0)

print datetime.now(tz=GMT8()).day
