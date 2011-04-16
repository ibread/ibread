#!/bin/bash
BASE="home/condor/cps210"
nohup sar -o ${BASE}/cpu 300 60 >/dev/null 2>&1 &
