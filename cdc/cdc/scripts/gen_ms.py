#!/usr/bin/env python
# Generate test bench file for ModelSim

import os, sys, re

if len(sys.argv) < 3:
    print "Usages: %s VERILOG PATTERN" % sys.argv[0]
    sys.exit(1)

filename = sys.argv[1]
pattern_file = sys.argv[2]
verilog_dir = os.path.dirname(os.path.abspath(filename))
struct_file = "%s/struct.info" % verilog_dir
scanchain_file = "%s/scanchain.info" % verilog_dir
recv_file = "%s/recv_dff.txt" % verilog_dir

# print pattern_file
r = re.findall(r'msr(\d+)_', pattern_file)
fault_num = r[0]

outputs = ""
definition = ""
extra_outs = ""

fin = open(filename)
start_flag = False
for line in fin:
    line = line.lstrip()
    
    if line.startswith('module ') and not line.startswith('module buf1'):
        start_flag = True
        r = re.findall(r'\((.*)\)', line)
        if len(r) > 0: 
            definition = r[0]
    if not start_flag:
        continue

    if line.strip().endswith('// extra outputs;'):
        line = line.strip().replace('// extra outputs;', '')
        line = line.split()[1]
        line = line.strip(' ;')
        extra_outs += ("TopTester.CUT." + line + ", ")

    if line.startswith('input'):
        outputs += line.replace('input ', 'reg ')
    elif line.startswith('output'):
        outputs += line.replace('output', 'wire')
    # elif line.startswith('wire'):
    #     outputs += line
fin.close()
extra_outs = extra_outs.rstrip(', ')

clks = []
outs = []

fin = open(struct_file)
for line in fin:
    line = line.strip()
    if line.startswith('clk '):
        line.replace('clk ', '')
        clks.extend(line.split())
    elif line.startswith('output '):
        line.replace('output ', '')
        outs.extend(line.split())
       
fin.close()

# open scanchain file to get the dff output
dff_out = {}
extra_outs_format = "\""
fin = open(scanchain_file)

for line in fin:
    # 1 dflipflop1 dff1_out
    line = line.split()
    dff_out[line[1]] = line[2]
    extra_outs_format += line[2]+"_old, "
fin.close()
extra_outs_format += "= \\n%b\""

lines = open(recv_file).readlines()
send_dff, recv_dff = lines[int(fault_num)-1].split()
send_dff_out = dff_out[send_dff]
recv_dff_out = dff_out[recv_dff]

test_vector = definition

i = 1
clks.append('scan_enable')
for clk in clks:
    if (' %s,' % clk) in test_vector:
        test_vector = test_vector.replace(' %s,' % clk, ' trash%d,' % i)
        outputs += "reg trash%s;\n" % i
        i += 1

# delete all outputs
for o in outs:
    r = re.compile(r'%s *,' % o)
    test_vector = r.sub('',test_vector)
    r = re.compile(r'%s *;' % o)
    test_vector = r.sub('',test_vector)

# print extra_outs
# print clks
# print definition
# print test_vector

format = '''
module TopTester ();

%(outputs)s

integer OutputFile;

// definition
new_module CUT (%(definition)s);

always #20 clk_i = ~clk_i;

initial begin
		
		clk_i = 1'b0; 
        scan_enable=1'b0;

	
 OutputFile =  $fopen("%(out_dir)s/msr1_f%(fault_num)s_p%(pattern_num)d.out", "w");
 $fdisplay(OutputFile, "results are as below:  ");

// $fscanf(InputVectorFile,"\\n%%b", testVector);

 {%(test_vector)s} = %(pi_dff_size)s'b%(vector_values)s; // only the inputs, but the order should be the same in the definition
			    
  
@(posedge clk_i);
@(posedge clk_i); $fdisplay(OutputFile, %(extra_outs_format)s, {%(extra_outs)s});

if(TopTester.CUT.%(recv_dff_out)s_old==1'b1) // && TopTester.CUT.%(send_dff_out)s_old==1'b0)
 begin
    $fdisplay (OutputFile, "Detected fault %(fault_num)s by vector %%b \\n", %(pi_init_size)s'b%(pi_init_values)s);
    $fdisplay (OutputFile, "PI=%%b\\n", %(pi_size)s'b%(pi)s);
    $fdisplay (OutputFile, "Init=%%b\\n", %(init_size)s'b%(init)s);
    $fdisplay (OutputFile, "ff results=%%b\\n", %(dff_size)s'b%(dff)s);
 end
else
 begin
    $fdisplay (OutputFile, "Not Detected fault %(fault_num)s by vector %%b \\n", %(pi_init_size)s'b%(pi_init_values)s);
    $fdisplay (OutputFile, "PI=%%b\\n", %(pi_size)s'b%(pi)s);
    $fdisplay (OutputFile, "Init=%%b\\n", %(init_size)s'b%(init)s);
    $fdisplay (OutputFile, "ff results=%%b\\n", %(dff_size)s'b%(dff)s);
 end

// $stop;
end
endmodule
'''

patterns = open(pattern_file).readlines()
# the format is like this
# init
# pi
# dff

pattern_dir = os.path.dirname(os.path.abspath(pattern_file))

os.system("mkdir -p %s" % (pattern_dir+"/bench"))
os.system("mkdir -p %s" % (pattern_dir+"/msout"))

num = len(patterns)/3
for i in xrange(num):
    init_size, init = patterns[3*i].split()
    pi_size, pi = patterns[3*i+1].split()
    dff_size, dff = patterns[3*i+2].split()
    f = open ("%s/bench/msr1_f%s_p%d.v" % (pattern_dir, fault_num, i+1), "w+")
    f.write(format % {'outputs':outputs, 'extra_outs':extra_outs, 'extra_outs_format':extra_outs_format, 'fault_num':fault_num, 'pattern_num':i+1, 'definition':definition, 'test_vector':test_vector, 'pi_init_values':pi+init, 'vector_values':pi+dff[::-1], 'pi':pi, 'dff':dff, 'init':init, 'recv_dff_out':recv_dff_out, 'out_dir':pattern_dir+"/msout", 'pi_size':pi_size, 'dff_size':dff_size, 'init_size':init_size, 'pi_init_size':int(pi_size)+int(init_size), 'pi_dff_size':int(pi_size)+int(dff_size), 'send_dff_out':send_dff_out})
    f.close()

