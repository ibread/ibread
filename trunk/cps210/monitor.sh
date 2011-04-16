#!/bin/bash
echo -e "\n=========$(date)========" >> mem.log
free -t -m  >> mem.log
# output ps information
echo -e "\n=========$(date)========" >> ps.log
ps -eo pcpu,size,vsize,cutime,cstime,utime,pid,user,args | sort -k 1 -r >> ps.log
echo -e "\n=========$(date)========" >> raw_ps.log
ps aux >> raw_ps.log
