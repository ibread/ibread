#!/usr/bin/python 
# change all sender_clk into clk_i

import os, sys, re

if len(sys.argv) < 4:
    print "Usage: FILENAME SENDER_DOMAIN RECEIVER_DOMAIN"
    print "The default values are used"
    print "  sender_clk "
    print "  clk_i"

file = sys.argv[1]
send = sys.argv[2]
recv = sys.argv[3]

new_file = file+".new"

fout = open(new_file, "w+")

for line in open(file):
    # replace sender with receiver if they start with DFF
    if line.strip().startswith('SDFF'):
        line = line.replace(send, recv)
    else:
        # remove ",  sender" in:
        # bla, bla, sender, haha;
        # bla, bla, sender;
        r = re.compile(r", *%s" % send)
        line = r.sub('', line)

        # remove "input   sender;"
        r = re.findall(r"input *%s *;" % send, line.strip())
        if len(r) != 0:
            line = ""

        # remove "sender ," in "input sender, haha, haha;"
        r = re.compile(r"sender *,")
        line = r.sub('', line)

    fout.write(line)


fout.close()

