#!/usr/bin/python
# @file: set_cover.py
# @author: Zhiqiu Kong <zk11@duke.edu>
# @usage:
#       ./set_cover.py DIR
#       DIR is the directory where all the results files reside. Every file contains test vectors for the corresponding fault.
#           For example, uresult_0.txt contains all vectors for fault 0
# @output:
#       The solving process will be printed out to the standard output (mostly the screen).
#       The selected set of vectors will be stored in "min_set_cover.txt", one vector a line.
# @brief:
#       This script is used to find a minimum set of test vectors to cover all the faults
#       Note that untestable faults will be ignored. (Empty result file)

import os, sys
import sets

if len(sys.argv) < 2:
    print "Usage: %s DIR" % sys.argv[0]
    sys.exit(1)

DIR = sys.argv[1]
file_list = os.listdir(DIR)

vector_set = {}

print "==============Scan vectors============="
faults = 0
for f in file_list:
    lines = open(os.path.abspath(DIR)+"/"+f, "r").readlines()

    for l in lines:
        try:
            vector_set[l.strip()].add(faults)
        except KeyError:
            vector_set[l.strip()] = set([faults])

    if len(lines) > 0:
        print "Set %d : %s" % (faults, f)
        faults += 1
    else:
        print "File %s is Empty, skipping" % f

print

print "==============Solving=============="
   
vs_list = []

for k in vector_set:
    v = vector_set[k]
    vs_list.append((k,v))

uncovered = set([i for i in xrange(faults)])
cover = []

index = 1

while len(uncovered) != 0:
    vs_list.sort(key=lambda x:len(x[1]), reverse=True)
    current = vs_list.pop(0)
    cover.append(current[0])
    uncovered.difference_update(current[1])
    print "%3d: %s" % (index, current)
    index += 1
    print "\tLeft...", uncovered
    for i in xrange(len(vs_list)):
        vs_list[i][1].difference_update(current[1])

    i = 0
    while i < len(vs_list):
        if len(vs_list[i][1]) == 0:
            vs_list.pop(i)
        else:
            i += 1

fout = open("min_set_cover.txt", "w+")
for c in cover:
    fout.write(c + "\n")

print 
print "Done. "
print "Plz check min_set_cover.txt for all the vectors selected"
