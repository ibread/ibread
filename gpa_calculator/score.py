#!/usr/bin/python

import sys, os

if len(sys.argv) < 2:
    print "No filename provided, score.txt is used"
    fin = "score.txt"
else:
    fin = sys.argv[1]

if not os.path.isfile(fin):
    print fin, "is not a valid file"
    print "Plz check it out."
    sys.exit(1)

score = 0.0
all = 0.0
for line in file(fin):
    if len(line.strip())==0 or line.strip()[0]=='#':
        continue
    score += float(line.split()[0])
    all += float(line.split()[0])*float(line.split()[1])

print float(all)/score
