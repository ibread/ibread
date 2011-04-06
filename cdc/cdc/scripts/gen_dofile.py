#!/usr/bin/python 

import os, sys

# please change this if you want other faults, this will appear as
# 0 UC g32/Y
fault_value = 0 

format = '''
// All the command should be inserted in this file
// Check fastscan help documents to get more information
// about the commands

// Add date to log files
system date

add clocks 0 clk_i  //important1

add scan group grp1 sample_clk.proc 
add scan chains chain10 grp1 scan_data_in scan_data_out

set z hand ext x

add nofaults SDFFNSR -module //important2
add nofaults SDFF -module 

add pin constraint scan_data_in C0
add pin constraint scan_enable C0

// Prevent transitions from Primary inputs during capture cycles.
set transition holdpi on

// Prevent measures on Primary outputs.
set output masks on

// To prevent transition paths from passing though a bidir pin.
flatten model
add slow pad -all

//set fault type stuck -DEtections 10
set fault type transition -no_shift_launch -DEtections 1000
// set fault type transition -DEtections 10
set pattern type -seq 2 -clock_po off 


set system mode atpg

// These command are to create log files
// Optional ...
report scan groups > scaninfo_fault1
report scan cells -all >> scaninfo_fault1
report drc rules -verbose -summary > drcinfo_fault1
// Add report commands if you want

// General ATPG - mode settings:
set split capture_cycle on

// Add all the faults
// add fault -all
delete faults -all
load faults f2_%(num)d //important3  in f2 was sender
//add faults /g31357/A -Stuck_at 0 
//add faults /scan_flop_1_5/Q
//add faults /g46/Y
//add faults /g32/Y
//add faults /g1/Y 
//delete faults /g1/Y 0
//delete fault 
// Create patterns

//add faults  /g400/A 
add atpg constraints 0 /%(dff)s/Q   //important4  reciever

create patterns -auto
//add atpg constraints 1 /scan_flop_1_8/Q
//add atpg constraints 0 /g19/Y

system date

write faults faults_list_%(num)d -replace  //important 5s

report statistics > stat/%(num)d.stat//ALL NAMES important5
report statistics
// Save your patterns to a file
save patterns %(num)d.pattern -Ascii -replace /ALL NAMES important5
// Exit Fastscan
exit -d
'''
try:
    fin = open("recv_dff.txt")
except IOError:
    print "Error openning recv_dff.txt, plz check it out"
    sys.exit(1)

lines = fin.readlines()

num = len(lines)# please change this into the number of cases

os.system("mkdir -p ./dofiles")

for i in xrange(num):
    dff = lines[i].split()
    if len(dff)==0 or dff[0] == "NO_SENDER" or dff[1] == "NO_RECV":
        print "Error in %dth dofile" % i
        continue
    print "outputting %d" % i
    f = open("./dofiles/%d.do" % i, "w+")
    f.write(format % {'num':i, 'dff':dff[1]})
    f.close()
    f = open("./dofiles/f2_%d" % i, "w+")
    f.write("%d UC %s/Q" % (fault_value, dff[0]))
    f.close()

fin.close()
