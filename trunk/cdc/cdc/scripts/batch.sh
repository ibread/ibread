#!/bin/bash
# @file: batch.sh
# @author: Zhiqiu Kong <zk11@duke.edu>
# @brief: Add fault into dofile, according to cdc_paths.txt where every line 
#           indicates a CDC path.
#         Then run fastscan to generate patterns.
#         Generated pattern file as well as log file will be archieved automatically.
# @usage:
#         ./batch.sh

while read line
do
    echo ${line}
    first=$(echo ${line} | cut -d" " -f1)
    second=$(echo ${line} | cut -d" " -f2)
    port=$(echo ${line} | cut -d" " -f3)
    sed -ie "s/^add faults.*$/add faults \/${second}\/${port} -Stuck_at 0/g" clk.do
    ./clk.run &> /dev/null
    cp log/clk.log cdc_logs/"${first}_${second}".log
    cp pattern/clk_i.pattern cdc_logs/"${first}_${second}".pattern
    cp faults_list cdc_logs/"${first}_${second}".faults
done < ./cdc_path.txt
