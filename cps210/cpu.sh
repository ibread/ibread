#!/bin/bash
BASE="/home/condor/cps210"
nohup sar -o ${BASE}/cpu 300 72 >/dev/null 2>&1 &
nohup top -b -d 5 &> ${BASE}/top & 
