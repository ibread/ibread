#!/usr/bin/env python
# Generate test bench file for ModelSim

import os, sys, re

if len(sys.argv) < 4:
    print "Usages: %s VERILOG PATTERN STRUCT" % sys.argv[0]
    sys.exit(1)
else:
    filename = sys.argv[1]
    pattern_file = sys.argv[2]
    struct_file = sys.argv[3]

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
        extra_outs += ("TopTester\\CUT\\" + line + ", ")

    if line.startswith('input'):
        outputs += line.replace('input', 'reg')
    elif line.startswith('output'):
        outputs += line.replace('output', 'wire')
    elif line.startswith('wire'):
        outputs += line
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


test_vector = definition

i = 1
for clk in clks:
    test_vector = test_vector.replace(' %s,' % clk, ' trash%d,' % i)
    i += 1

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

integer OutputFile,InputVectorFile;

// definition
new_module CUT (%(definition)s);

always #20 clk_i = ~clk_i;

initial begin
		
		clk_i = 1'b0; 

	
 OutputFile =  $fopen("msr1_%(fault_num)s_%(pattern_num)d.out", "w");
 $fdisplay(OutputFile, "results are as below:  ");

// $fscanf(InputVectorFile,"\\n%%b", testVector);

 {%(test_vector)s} = %(vector_values)s; // only the inputs, but the order should be the same in the definition
			    
  
//@(posedge clk_i); $display("out1 = %%b", out1);
@(posedge clk_i); $fdisplay(OutputFile, "flipflops = %%b", {%(extra_outs)s});

 //$stop;
end
endmodule
'''

patterns = open(pattern_file).readlines()

os.system("mkdir bench")

num = len(patterns)/2
for i in xrange(num):
    pi = patterns[2*i].split()[1]
    dff = patterns[2*i+1].split()[1][::-1]
    f = open ("./bench/msr1_%s_%d.bench" % (fault_num, i+1), "w+")
    f.write(format % {'outputs':outputs, 'extra_outs':extra_outs, 'fault_num':fault_num, 'pattern_num':i+1, 'definition':definition, 'test_vector':test_vector, 'vector_values':pi+dff})
    f.close()

