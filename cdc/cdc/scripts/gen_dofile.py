#!/usr/bin/python 

import os, sys

if len(sys.argv) < 2:
    print "Usage: %s VERILOG_FILE"
    sys.exit(1)

# this is the verilog we need to run fastscan, like bla_mux_inserted_fastscan.v
VERILOG = os.path.abspath(sys.argv[1])

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

add scan group grp1 /home/vishwanagarik/nk86/ICCD/sample_clk.proc 
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
set fault type transition -no_shift_launch -DEtections 10
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

report statistics > %(num)d.stat//ALL NAMES important5
report statistics
// Save your patterns to a file
save patterns %(num)d.pattern -Ascii -replace //ALL NAMES important5
// Exit Fastscan
exit -d
'''

run_format = '''
#!/usr/bin/python
import os, sys

os.system("/home/software/mentor/2007/linux64/dft_2007_1_10/bin/fastscan -nogui -verilog -64 -replace %(VERILOG)s -top new_module -lib /home/vishwanagarik/nk86/ICCD/gsc.atpg -dof %(DOFILE)s -log log/clk.log &> temp")

'''


try:
    fin = open("recv_dff.txt")
except IOError:
    print "Error openning recv_dff.txt, plz check it out"
    sys.exit(1)

lines = fin.readlines()

num = len(lines)# please change this into the number of cases

os.system("mkdir -p ./dofiles")
os.system("mkdir -p ./runfiles")

for i in xrange(1, num+1):
    dff = lines[i-1].split()
    if len(dff)==0 or dff[0] == "NO_SENDER" or dff[1] == "NO_RECV":
        print "Error in %dth dofile" % i
        continue
    print "outputting %d" % i
    
    # create do files
    f = open("./dofiles/%d.do" % i, "w+")
    f.write(format % {'num':i, 'dff':dff[1]})
    f.close()
    
    # create f2 files
    f = open("./dofiles/f2_%d" % i, "w+")
    f.write("%d UC %s/Q" % (fault_value, dff[0]))
    f.close()

    # create fun files
    f = open("./runfiles/run_%d.py" % i, "w+")
    f.write(run_format % {'VERILOG':VERILOG, 'DOFILE':'%d.do'%i })
    f.close()

fin.close()
