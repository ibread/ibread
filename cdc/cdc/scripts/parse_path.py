#!/usr/bin/env python
# @file: parse_path.py
# @author: Zhiqiu Kong <zk11@duke.edu>
# @brief: This script is used to parse CDC path and assign values to each input of each combinational gate 
#           on the path.
#         This is done basing on the output value we need, and also they type of each combinational gate.
#         We need to make sure:
#           1. Get the output value we need to assign to the output of DFF1 (in the sender domain)
#           2. The value of inputs of every combinational gates are assigned carefully to make sure that the value of output
#           of DFF1 could be passed into receiver domain.
#         
#         After each input is assigned a value, we insert corresponding contraint into dofile to make sure the pattern
#           generated will help us to achieve this.
#
#         Two problem are encountered when we do this:
#           1. Constaints could be added into dofile by using the following statements:
#                add pin constraint /g31104/B C0
#              This is used to enforce the pin 'B' of gate 'g31104' is assigned as 0 by the pattern generated.
#              But the problem is that fastscan do not accept constraint added into non-primary input.
#              This is solved by adding another statement, 
#                 add primary input -internal /g31104/B
#              The statement is used to add the internal pin as primary input.
#              TO-DO: But I'm not sure if this will cause some violations. More data are necessary to verify this.
#           2. Some of the pins are already primary inputs after splitting the circuits. Thus, fastscan will complain
#              if some pins are already primary inputs because we use the following statemewnt
#                 add primary input -internal /g31104/B
#              This is solved by parsing the verilog netlist where we need to generate constraints for.
#               Primary inputs information will be extracted and we could check if the pin is already primary input.
#               Note that the verilog is the circuit after splitting.
#   
# @usage: ./parse_path PATH_FILE VERILOG_FILE OUT_VALUE
#   PATH_FILE: The file containing CDC path. Every line in the file is a CDC path as following:
#               g29896:Y(n_11202) --  u1_slt2_reg_b19_b[bit_clk_pad_i] ===> g40434 [MX2X1 @ clk_i]:B(pi:in_slt_845) ===> u15_crac_din_reg_b15_b[clk_i](n_1083) -- g37365:B1
#              Its format is:
#               * Clock is enclosed in [], such as [bit_clk_pad_i] and [clk_i]. We need this to make sure that it is a real CDC path.
#               * Type of the combinational gate is also enclosed in [], before @, if necessary. Such as [MX2X1 @ clk_i], denotes it is a MUX.
#                   We need this for reasoning and assign correct value to each pin of each combinational gate. 
#               * Pin name is enclosed in (), such as (n_11202). This is the input of the gate which is on the CDC path. 
#                   This is necessary because we need to assign each pin a value and write the contraint into dofile.
#                   If this pin is a primary output, there will be 'pi' before the name of the pin, separated with it using ':', such as (pi:in_slt_845) means that 
#                   in_slt_845 is a primary input in the circuits
#               * Pin name in the definition of the gate is put exatly before (). Such as B(pi:in_slt_845) means in_slt_845 is 'B' pin of the MUX. 
#               * Gates on the CDC path, including DFFs at both ends, are connected by '===>'.
#               * The combinational gates before '--' and after '--' is the ones directly connected to DFFs. 
#                   We need this information because we need to add fault into pins of these combinational gates.
#                   This is because test pattern could not be generated for outputs of the DFFs. We need to insert fault into output/input of combinational gates directly
#                   connected with DFFs as a workaround.
#                   It is possible that DFFs connects to none of the combinatioanl gate. But these cases are few.
#  VERILOG_FILE: The verilog net list. This is the circuit we need to inject fault and contraints to generate a pattern.
#               Note that this should be the circuit after splitting according to clock domain instead of the original one.
#               Also note that we need this script only for the receiver domain.
#  OUT_VALUE:   This denote the fault type we need to insert into the circuit, but not exactly the same. 
#               For example, if we need to generate pattern for s-a-0 fault, we need 1 passed from the sender domain. Before that we should keep the value as 0.
#               Then 0 should be the OUT_VALUE.
#               
# @output:
#       The output is directly pushed into the standard output. Output redirection could be used to write them into a file.
#       Every path in the PATH_FILE is parsed to output all constraints we need to add into dofile. Here is one example of the ouptut: 
#
#          ===================729=================
#          g35371:Y(n_6728) --  u1_slt4_reg_b0_b[bit_clk_pad_i] ===> g39870 [NAND2X1 @ clk_i]:B(pi:in_slt4) ===> g37156 [NAND2X1 @ clk_i]:B(n_2236) ===> g36154 [MX2X1 @ clk_i]:B(n_5997) ===> g31280 [MX2X1 @ clk_i]:A(n_5960) ===> u10_mem_reg_b0_b_b0_b[clk_i](n_10138) -- g42437:A
#          
#          add primary input -internal /g31280/A
#          add pin constraint /g31280/A C1
#          add primary input -internal /g31280/B
#          add pin constraint /g31280/B C0
#          add primary input -internal /g31280/S0
#          add pin constraint /g31280/S0 C0
#          add primary input -internal /g36154/A
#          add pin constraint /g36154/A C0
#          add primary input -internal /g36154/B
#          add pin constraint /g36154/B C1
#          add primary input -internal /g36154/S0
#          add pin constraint /g36154/S0 C1
#          add primary input -internal /g37156/A
#          add pin constraint /g37156/A C1
#          add primary input -internal /g37156/B
#          add pin constraint /g37156/B C0
#          add primary input -internal /g39870/A
#          add pin constraint /g39870/A C1
#          add pin constraint /g39870/B C1
#          For sender domain g35371:Y(n_6728) --  u1_slt4_reg_b0_b[bit_clk_pad_i] 1
#          ===================730=================
#
#       The original path is firstly output where the format is explained above. 
#       Then comes all constraints we needed. Note that "add primary input" is not used with every pin, this is because it is already a primary input.
#       Finally, the fault type to add into the sender domain is also output. For exmaple,
#          For sender domain g35371:Y(n_6728) --  u1_slt4_reg_b0_b[bit_clk_pad_i] 1
#       This denotes that s-a-1 should be added into /g35371/Y
#       Also, we should add constraint to u1_slt4_reg_b0_b/bit_clk_pad_i to make sure it is 1.
#

import os, sys
import re

def get_info(dev_name, out_value, input):
    '''
        Given device type and output, return device input 
    '''

    if out_value != 0 and out_value != 1:
        print "[Error] out_value should be 0/1 instead of %s" % out_value
        return None

    dev_model = {"CLKBUFX1":('BUF', 'A', 'Y'), \
                 'CLKBUFX2':('BUF', 'A', 'Y'), \
                 'CLKBUFX3':('BUF', 'A', 'Y'), \
                 'BUFX3':('BUF', 'A', 'Y'), \
                 'INVX1':('INV', 'A', 'Y'), \
                 'INVX2':('INV', 'A', 'Y'), \
                 'INVX4':('INV', 'A', 'Y'), \
                 'INVX8':('INV', 'A', 'Y'), \
                 'AND2X1':('AND', 'A', 'B', 'Y'), \
                 'OR2X1':('OR', 'A', 'B', 'Y'), \
                 'NAND2X1':('NAND', 'A', 'B', 'Y'), \
                 'NAND2X2':('NAND', 'A', 'B', 'C', 'Y'), \
                 'NAND3X1':('NAND', 'A', 'B', 'C', 'Y'), \
                 'NAND4X1':('NAND', 'A', 'B', 'C', 'D', 'Y'), \
                 'NOR2X1':('NAND', 'A', 'B', 'Y'), \
                 'NOR3X1':('NAND', 'A', 'B', 'C', 'Y'), \
                 'XOR2X1':('NOR', 'A', 'B', 'Y'), \
                 'AOI21X1':('AOI1', 'A0', 'A1', 'B0', 'Y'), \
                 'AOI22X1':('AOI2', 'A0', 'A1', 'B0', 'B1', 'Y'), \
                 'OAI21X1':('OAI1', 'A0', 'A1', 'B0', 'Y'), \
                 'OAI22X1':('OAI2', 'A0', 'A1', 'B0', 'B1', 'Y'), \
                 'MX2X1':('MUX', 'S0', 'A', 'B', 'Y'), \
                 'ADDHX1':('ADD', 'A', 'B', 'CO', 'Y'), \
                 'DFFX1':('DFF', 'CK', 'D', 'Q', 'QN'), \
                 'DFFSRX1':('DFF', 'CK', 'RN', 'SN', 'D', 'Q', 'QN') \
                 }
    try:
        raw = dev_model[dev_name]
    except KeyError:
        print "Error, key %s not found" % dev_name
        return None

    dev_type = raw[0]
    out_name = raw[-1]
    input_name = raw[1:-1]
    
    ret = {}
    if dev_type == 'BUF':
        ret['A'] = out_value
    elif dev_type == 'INV':
        ret['A'] = 1-out_value 
    elif dev_type == 'AND':
        if out_value == 0:
            # if out_value is 0, and it is AND gate
            # other inputs ports other than 'input' should be 1
            # 0 should be propagated by 'input'
            for i in input_name:
                if i == input:
                    ret[i] = 0
                else:
                    ret[i] = 1
        else:
            for i in input_name:
                ret[i] = 1
    elif dev_type == 'OR':
        if out_value == 1:
            # if out_value is 1, and it is OR gate
            # other inputs ports other than 'input' should be 0
            # 1 should be propagated by 'input'
            for i in input_name:
                if i == input:
                    ret[i] = 1
                else:
                    ret[i] = 0
        else:
            for i in input_name:
                ret[i] = 0
    elif dev_type == 'NAND':
        if out_value == 1:
            # if out_value is 1, and it is NAND gate
            # other inputs ports other than 'input' should be 1
            # 0 should be propagated by 'input'
            for i in input_name:
                if i == input:
                    ret[i] = 0
                else:
                    ret[i] = 1
        else:
            for i in input_name:
                ret[i] = 1
    elif dev_type == 'NOR':
        if out_value == 0:
            # if out_value is 1, and it is NAND gate
            # other inputs ports other than 'input' should be 1
            # 0 should be propagated by 'input'
            for i in input_name:
                if i == input:
                    ret[i] = 1
                else:
                    ret[i] = 0
        else:
            for i in input_name:
                ret[i] = 0
    elif dev_type == 'MUX':
        if input == 'A':
            ret['S0'] = 0
            ret['A'] = out_value
            #ret['B'] = 1-out_value
        elif input == 'B':
            ret['S0'] = 1
            #ret['A'] = 1-out_value
            ret['B'] = out_value
    elif dev_type == 'AOI1' or dev_type == 'AOI2':
        # 'AOI21X1':('AOI1', 'A0', 'A1', 'B0', 'Y'), \ #Y=!((A&B)|C)
        # 'AOI22X1':('AOI2', 'A0', 'A1', 'B0', 'B1', 'Y'), \ #Y=!((A&B)|(C&D))
        if out_value == 0:
            initial = input[0]
            for i in input_name:
                if i.startswith(initial):
                    ret[i] = 1
                else:
                    ret[i] = 0
        else:
           for i in input_name:
                if i == input: 
                    ret[i] = 0
                elif i[0] == input[0]:
                    ret[i] = 1
                elif i[0] != input[0]:
                    ret[i] = int(i[1])
    elif dev_type == 'OAI1' or dev_type == 'OAI2':
        # 'OAI21X1':('OAI1', 'A0', 'A1', 'B0', 'Y'), \ #Y=!((A|B)&C)
        # 'OAI22X1':('OAI2', 'A0', 'A1', 'B0', 'B1', 'Y'), \ #Y=!((A|B)&(C|D))
        if out_value == 1:
            initial = input[0]
            for i in input_name:
                if i.startswith(initial):
                    ret[i] = 0
                else:
                    ret[i] = 1
        else:
           for i in input_name:
                if i == input: 
                    ret[i] = 1
                elif i[0] == input[0]:
                    ret[i] = 0
                elif i[0] != input[0]:
                    ret[i] = int(i[1])

    return ret
    
def get_pin_info(vname):
    '''
        Parse verilog file
        return one list and one dict:
        input_list: list of primary input
        dev_dict: {dev_name:{port:name}}, such as {g3157:{A:in_slt_745}}
    '''

    input_list = []
    dev_dict = {}

    try:
        fin = open(vname)
    except IOError:
        print "Error openning %s" % vname

    state = ""

    inside = False
    
    for line in fin:
        line = line.strip()
        # print "line:", line

        # we should not deal with statements in module buf1
        if line.startswith("module buf1"):
            inside = True
            continue
        elif line.startswith("endmodule"):
            inside = False
            state = ""
            continue

        if inside:
            continue

        
        # skip comments
        if not line or line.startswith('//'):
            continue
    
        state += line.strip()
        
        if not state.endswith(';'):
            continue


        if state.split()[0] == "input":
            inputs = state.replace('input ', '').strip(' ;')
            inputs = map(lambda x:x.strip(), inputs.split(','))
            input_list.extend(inputs)
            state = ''
            continue
            
        if state.split()[0] not in ["buf1", "module", "input", "output", "wire"]:
            # print "*", state, "*"
           
            # sample state 
            # NAND2X1 g34598(.A (u6_mem_b1_b ), .B (n_7758), .Y (n_7832));
            # NAND2X1
            dev_type = state.split()[0]

            # g34598(.A(u6_mem_b1_b),.B(n_7758),.Y(n_7832));
            others = ''.join(state.split()[1:])

            # g34598, .A(u6_mem_b1_b),.B(n_7758),.Y(n_7832)
            results = re.findall(r'(.+?)\((.*)\)', others)
            
            if len(results) == 0:
                print "[Error] no device name in %s" % others
            
            results = results[0]

            # g34598
            dev_name = results[0]
            # .A(u6_mem_b1_b),.B(n_7758),.Y(n_7832)
            all_ports = results[1]

            dev_dict[dev_name] = {}

            results = re.findall(r'\.([^(]+)\((.+?)\)[,]*', all_ports)
            if len(results) == 0:
                print state
                print state.split()[0]
                print "[Error] no port in %s" % all_ports

            for r in results:
                pin_port = r[0]
                pin_name = r[1]
                dev_dict[dev_name][pin_port] = pin_name
                

        state = ""

    #print pin_name_dict
    return input_list, dev_dict


def parse(verilog="clk_i.v", out_value = 1):
    '''
    '''

    verilog_name = verilog
    #out_value = 1 # for hold-time violation, and stuck-at-0 faults

    if len(sys.argv) <= 3:
        print "Usage: %s PATH_FILE VERILOG_FILE OUT_VALUE" % sys.argv[0]
        sys.exit(1)

    path_file = sys.argv[1]
    verilog_name = sys.argv[2]
    out_value = int(sys.argv[3])

    try:
        f = open(path_file)
    except IOError:
        print "Error openning %s" % path_file
        sys.exit(1)

    input_list, dev_dict = get_pin_info(verilog_name)
    #print input_list, 'in_slt_415' in input_list


    count = 0
    for path in f:
        # the path's format is like this
        # path = "g29897:Y(n_11201) --  u1_slt3_reg_b19_b[bit_clk_pad_i] ===> g31357 [MX2X1 @ clk_i]:B(pi:in_slt_415) ===> u9_din_tmp1_reg_b15_b[clk_i](n_9780) -- g31357:A"
        # path = "g29896:Y(n_11202) --  u1_slt2_reg_b19_b[bit_clk_pad_i] ===> g40434 [MX2X1 @ clk_i]:B(pi:in_slt_845) ===> u15_crac_din_reg_b15_b[clk_i](n_1083) -- g37365:B1"

        print "===================%s=================" % count
        count += 1
        print path

        paths = map(lambda x: x.strip(), path.split('===>'))
        i = len(paths)-2
        while i >= 1:
            p = paths[i]
            # print p
            # get pin name, like in_slt_415 in g37661 [AOI22X1 @ clk_i]:B0(in_slt_415)
            pin_name = re.findall(r'\]:.*?\((.+)\)', p)
            if len(pin_name) == 0:
                print "[Error] no pin name in %s" % p

            # get port name, like B0 in g37661 [AOI22X1 @ clk_i]:B0(in_slt_415)
            input = re.findall(r':([^ ]+)\(', p)
            if len(input) == 0:
                print "[Error] No port name in %s" % p
            input = input[0]

            # get device type, like AOI22X1 in g37661 [AOI22X1 @ clk_i]:B0(in_slt_415)
            dev_type= re.findall(r'\[(.+) @', p)
            if len(dev_type) == 0:
                print "[Error] No device type in %s" % p
            dev_type = dev_type[0]

            # get device name, like g37661 in g37661 [AOI22X1 @ clk_i]:B0(in_slt_415)
            dev_name = re.findall(r'([^ ]+).*\[', p)
            if len(dev_name) == 0:
                print "[Error] No port name in %s" % p
            dev_name = dev_name[0] 

            assign = get_info(dev_type, out_value, input)
            #print assign
            for k in assign.keys():
                # we need to determine that if /dev_name/k is already a input
                pin_name = dev_dict[dev_name][k]
                # print pin_name, pin_name in input_list
                if pin_name not in input_list:
                    print "add primary input -internal /%s/%s" % (dev_name, k)
                print "add pin constraint /%s/%s C%s" % (dev_name, k, assign[k]) 
            out_value = assign[input]

            i -= 1
        print "For sender domain", paths[0], out_value

if __name__ == '__main__':
    parse()
