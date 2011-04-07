#/usr/bin/env python
# Generate test bench file for ModelSim

import os, sys, re

if len(sys.argv) < 2:
    print "Usages: %s FILENAME" % sys.argv[0]
    print "The default filename new_mux_inserted.v is used"
    filename = "new_mux_inserted.v"
else:
    filename = sys.argv[1]

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

    if line.strip().endswith('// extra outputs'):
        line = line.strip().replace('// extra outputs', '')
        line = line.replace('wire ', '')
        line = line.strip(' ;')
        extra_outs += (line + ", ")

    if line.startswith('input'):
        outputs += line.replace('input', 'reg')
    elif line.startswith('output'):
        outputs += line.replace('output', 'wire')
    elif line.startswith('wire'):
        outputs += line

fin.close()

clks = []

fin = open("struct.info")
for line in fin:
    line = line.strip()
    if line.startswith('clk '):
        line.replace('clk ', '')
        clks.extend(line.split())
fin.close()

extra_outs = extra_outs.rstrip(', ')

test_vector = definition

i = 1
for clk in clks:
    test_vector = test_vector.replace(' %s,' % clk, ' trash%d,' % i)
    i += 1
    
# print extra_outs
# print clks
# print definition
# print test_vector

format = '''
module TopTester ();

%(outputs)s

integer OutputFile,InputVectorFile;

// definition
sample_circuit new_module (%(extra_outs)s, %(definition)s);

always #20 clk_i = ~clk_i;

initial begin
		
		clk_i = 1'b0; 

	
 OutputFile =  $fopen("msr1_%(num)d.out", "w");
 InputVectorFile =  $fopen("msr1_%(num)d.pattern", "r");
 $fdisplay(OutputFile, "results are as below:  ");

 $fscanf(InputVectorFile,"\n%%b", testVector);

 {%(test_vector)s} = testVector; // only the inputs, but the order should be the same in the definition
			    
  
//@(posedge clk_i); $display("out1 = %%b", out1);
@(posedge clk_i); $fdisplay(OutputFile, "flipflops = %%b", {%(extra_outs)s});

 //$stop;
end
endmodule
'''


num = len(open("recv_dff.txt").readlines())
for i in xrange(num):
    f = open ("ms%d.bench" % (i+1), "w+")
    f.write(format % {'outputs':outputs, 'extra_outs':extra_outs, 'num':i+1, 'definition':definition, 'test_vector':test_vector})
    f.close()

