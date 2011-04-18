#!/bin/bash
BASE="/home/condor/cps210"
echo -e "\n=========$(date)========" >> ${BASE}/mem.log
free -t -m  >> ${BASE}/mem.log
# output ps information
echo -e "\n=========$(date)========" >> ${BASE}/ps.log
ps -eo pcpu,size,vsize,cutime,cstime,utime,pid,user,args | sort -k 1 -r >> ${BASE}/ps.log
echo -e "\n=========$(date)========" >> ${BASE}/raw_ps.log
ps aux >> ${BASE}/raw_ps.log
echo -e "\n=========$(date)========" >> ${BASE}/iostat.log
iostat >> ${BASE}/iostat.log
