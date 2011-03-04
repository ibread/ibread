
// All the command should be inserted in this file
// Check fastscan help documents to get more information
// about the commands

// Add date to log files
system date

// clock and scan information
add clocks 0 clk_i
add scan group grp1 clk.proc
add scan chains chain10 grp1 scan_data_in scan_data_out

set z hand ext x

// add nofaults SDFFNSR -module

// Add pin constraints to disable testing of scan structures
// add pin constraint scan_data_in C0
// add pin constraint scan_enable C0
// Begin adding primary inputs
add primary input -internal /g31104/A
add pin constraint /g31104/A C1
add primary input -internal /g31104/B
add pin constraint /g31104/B C0
add primary input -internal /g31104/S0
add pin constraint /g31104/S0 C0
// End adding primary inputs

// Prevent transitions from Primary inputs during capture cycles.
set transition holdpi on

// Prevent measures on Primary outputs.
set output masks on

// Checkpointing
setup checkpoint pattern/s298_cdc.pattern.checkpoint 30 -Ascii -Replace
set checkpoint on

// To prevent transition paths from passing though a bidir pin.
flatten model
add slow pad -all

set fault type stuck -DEtections 1
// set fault type transition -no_shift_launch -DEtections 1
set pattern type -seq 2 -clock_po off

// If you want to add more processors
// Add the remaining processors of pabda
Add Processors pabda:7

// Put FastScan into ATPG mode which will execute the DRC checks
// and will allow test generation commands:
set system mode atpg

// These command are to create log files
// Optional ...
report scan groups > scaninfo
report scan cells -all >> scaninfo
report drc rules -verbose -summary > drcinfo
// Add report commands if you want

// General ATPG - mode settings:
set split capture_cycle on

// Add all the faults
// add fault -all
add faults /g31357/A -Stuck_at 0

// Create patterns
create patterns -auto
system date

// Report ATPG untestable faults
// Report Faults -class AU
// Report Untestable faults (UU+TI+BL+RE)
// UU UNUsed
// TI TIed
// BL Blocked
// RE Redundant
// Report Faults -class UT
write faults faults_list -replace

// Report statistics
report statistics > stat/clk_i.stat
report statistics
// Save your patterns to a file
save patterns pattern/clk_i.pattern -Ascii -replace
// Exit Fastscan
exit -d
