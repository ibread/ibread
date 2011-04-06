#!/usr/bin/python
# @File: cdc.py
# @Author: Zhiqiu Kong <zk11@duke.edu>
# @Brief:
#   1. Parse the original verilog netlist to get statistical information
#           Such as the types of all gates, number of gates, input/output dictionary for every gate
#           DFF list, etc.
#   2. Split the original verilog netlist into serveral sub netlist according to the clock domain
#           The gates (includings DFFs and combinational gates) in the same clock domain will
#           be put in the same sub verilog file
#   3. Analyaze to get DFFs at clock boundaries, as well as the CDC path.
#           This is done by traversing the circuits as in a graph.
#           The CDC path is output via standard output for the flexibility of handling.
# @Usage:
#   ./cdc.py VERILOG_FILE
#       Note that VERILOG_FILE should be the original verilog netlist, such as ac97_ctrl.v
#       After the command above is invoked, please wait for the output on the standard output.
#       There will be progress prompt to indicate which step it is in now, such as:
#       Here is the sample output.
#          ===================bit_clk_pad_i begins===================
#          ===================bit_clk_pad_i ends===================
#          ===================clk_i begins===================
#          ===================clk_i ends===================
#          g29896:Y(n_11202) --  u1_slt2_reg_b19_b[bit_clk_pad_i] ===> g40434 [MX2X1 @ clk_i]:B(pi:in_slt_845) ===> u15_crac_din_reg_b15_b[clk_i](n_1083) -- g37365:B1
#      While the program is running, you'll be noticed that which clock domain is under processing. After all 
#      clock domain is processed, CDC paths will be output which could be redirected into to file for futher usage  
#   
# @Problems:
#   1. After splitting, need to reparse to get primary inputs and ouptuts
#       some inputs are arrays, such as " input a[3]"
#       not sure if "input a[0], a[1], a[2]" works or not
#       
#       it turns out that it does not work, verilog does not allow we define primary inputs like this.
#       finally sloved by convert every element in an array into a independent variable
#       such as, in_slt[0] => in_slt_b_0_b
#
#   2. Some gates attach to none DFFs, do not know how to assign clocks to them
#           it is solved by traverse from every DFF, just as traverse a graph.
#   
#   3. Although we traverse each DFF until it encounters another DFF, it is found that a lot of gates
#       are without clock domain after we complete all the traversals.
#
#      This is possibily because that if we look into the circuits from the primary inputs, some gates are before all DFFs.
#       These gates could not be traversed because we traverse each DFF from its output. So the gates at the upstream of all DFFs
#       could not be touched.
#      This is finally sovled by using both directions while traversing. For example, for each DFF, we do not only traverse from 
#       its output to its downstream, but also from all its inputs to its upstream.
#
#   4.  After we split the circuits according to domain, pattern could not be generated for the output of DFF at clock boundary.
#       According to fastscan, the faults at these places are not testable. This is made sure after several tries.
#      
#       This is finally solved by finding combinational gate after the DFF whose output is the fault location.
#       This solution is reasonable because we care only the CDC faults, by which we assume that no faults are on the wire between 
#       the DFF and the combinational gate behind it.
#       But there are some problems because there might not be combinational gates after DFFs. But these gates are few.
#      
#   5. The scan chain is blocked at some DFF. It is suggested that there might be some combinational logic between two DFFs which both
#         are in the scan chain. Or I forgot to add some DFFs into the scan chain.
#       Both these causes are eliminated after double checks. The DFFs in the same domain are all found out and connected together according
#       to their clock domains. I check the total number of all DFFs and found no one is left.
#
#       Thanks to Mahmut for the final solution. It is found out that I should change the definition in ATPG library. The modification will 
#       help to copy Q port into another port QB, which could be used when connecting all DFFs into a scan chain. It is suggested that the 
#       functional ports should be splitted from the ports for scan chain.
#
#        model SDFFN (D, SI, SE, ST, RT, CK, Q, QB) (
#                cell_type = SCANCELL CK D;
#                scan_definition (
#                        type = mux_scan;
#                        data_in = D;
#                        scan_in = SI;
#                        scan_enable = SE;
#                        scan_out = QB;
#                )       
#                input (D, SI, SE, ST, RT) ()
#                input (CK) (clock = rise_edge;)
#                intern(_D) (primitive = _mux (D, SI, SE, _D);)
#                output(Q)  (primitive = _dff(ST, RT, CK, _D, Q, );)
#                output(QB)  (primitive = _dff(ST, RT, CK, _D, Q, );)
#        )
#
#
#       Also I should ensure that the set/reset signal into 0'b0
#
#   6. While the pattern is generated part by part in different clock domains, the first half of the pattern could not be generated independently.
#       To be more specific, the fault in the sender domain is determined by the combinational logic between the DFFs at clock boundary.
#       For example, after generating pattern for s-a-0 fault at output of DFF2, we should make sure that there is a '1' passed from the sender domain.
#       In order to do this, we need to generate pattern for s-a-0 fault at the output of DFF1, which is in the sender domain. But it is not true if there 
#       is a inverter between DFF1 and DFF2. 
#   
#       Also, the inputs of combinational gates on the path should be carefully set to ensure that '1' is passed from the sender domain. For exmaple, if there
#       is an AND gate on the path and we need to generate a '0' in the sender domain. We need to make sure the other inputs of the AND gate are all '1', otherwise
#       we could not be sure that the generated '0' at the output of the AND gate is because of the DFF in sender domain.
#
#       Thus, we need to parse the CDC path, assign values to each input of each combinational gate according to its type, and also the value needed as the output.
#       This part of work is completed by another script


RECV_DOMAIN = "clk_i"

import os, sys, re
from sets import Set

if len(sys.argv) < 2:
    print "Usages: %s FILENAME" % sys.argv[0]
    sys.exit(1)

source = sys.argv[1]

def _py230orlower():
    return sys.hexversion <= 0x20304f0

if _py230orlower():
    from sets import Set as set

# This class is used to represent a gate in the circuits
class node:
    name = "default"
    input = []
    output = []
    
    def __init__(self, name, input, output):
        self.name = name
        self.input = input
        self.output = output
        
# This class is used to represent a DFF in the circuits
class DFF:
    def __init__(self, d, q, qn, clk):
        self.d = d
        self.q = q
        self.qn = qn
        self.clk = clk

def gen_pins(pins, prefix):
    '''
    Given a list of pins like
        G0, G1, G2
    Return send_G0, send_G1, send_G2
        or
           recv_G0, recv_G1, recv_G2
    '''
    #prefix = sender and "send_" or "recv_"
    return ', '.join(map(lambda x: "%s_%s" % (prefix, x), pins))

def gen_dofile():
    '''
    Generate dofile
    '''

    # 1. Find DFFs at clock boundaries, these in Sender Domain are denoted as MID_DFFk(.D(s), .Q(r)), where k is the index.
    #      The ones connected to MID_DFFk could be found by checking .D(r), the DFF is denoted as REC( .D(r), .Q(t))
    # 2. Generate test pattern for slow-to-rise transition fault @ t. And according to this pattern, we could get what r is.
    # 3. Generate test pattern for stuck-at-0 fault @ s, with constraint that r is 0
    pass
    
#end of gen_dofile

def get_by_regex(pattern, string):
    '''
        Given a pattern and string, return the result by regex matching.
        This is used to parse the verilog and extract every input and output pin of the gates
    '''
    
    s = re.findall(pattern, string)
    
    if len(s) == 0:
        return None
    else:
        return s[0]

def process():
    '''
        Given the source file, which is verilog netlist. The following several things are done:
        1. Parse the file to get basic information of every gate
        2. Get statistical information of every gate, such as the amount of gate in differnt type
        3. Analyze the circuits to assign each gate a clock domain. 
            For DFF, this is easy to be done. We could assign the clock of the DFF to itself
            For combinational gates, we need to traverse each gate 
    '''
    try:
        fin = open(source)
    except IOError:
        print "Error openning %s, plz check it out." % source
        
    inside = False
    state = ""
    # device_type:device_number
    device = {}
    
    # device_name:device_type
    type_dict = {}
    
    # output lookup table, output : device_name
    out_dict = {}
    
    #input lookup table, input: device_name
    in_dict = {}
    in_dict_port = {}
    
    # device_name:output
    dev_out = {}
    # device_name: list(input)
    dev_in = {}
    dev_in_port = {}
    
    # clk: list(dff)
    clk_dff = {}
    
    # assigns
    # for the statement like 
    # assign wb_err_o = 1'b0;
    assigns = {}
    
    # for every dff, there is a clock attached
    # for other device, the clock is assigned by the one of the dff which 
    # is upstream of it
    dev_clk = {} # dev:clk
    dev_state = {} # dev:statement

    # primary inputs
    pri_ins = []
    # primary outputs
    pri_outs = []
    
    # each time a device is assigned a clock
    # there must be a dff driving it, which is called as origin
    dev_origin = {}
    
    # list( (send_clk, send_dff, recv_dff) )
    ck_bound = []
    # list(dff)
    dffs_list = []

    # the successor of every DFF, should be non-DFF
    # we need this because fastscan won't give the pattern for fault at output of DFF
    succ_dev = {}
    succ_port = {}

    for line in fin:
        
        if line.startswith("module"):
            inside = True
        elif line.startswith("endmodule"):
            inside = False
        
        # skip comments
        if not line or line.strip().startswith('//'):
            # print "##Comment: %s" % line
            continue
    
        state += line.strip()
        
        if not state.endswith(';'):
            continue

        # parse to get primary inputs
        if state.split()[0] == "input":
            inputs = ''.join(state.split()[1:])
            inputs = inputs.replace(' ', '')
            inputs = inputs.split(',')
            for i in inputs:
                i = i.strip(',;')
                p = re.compile(r"\[.*\]")
                i = p.sub('', i)
                pri_ins.append(i)
                
        if state.split()[0] == "output":
            outputs= ''.join(state.split()[1:])
            outputs= outputs.replace(' ', '')
            outputs= outputs.split(',')
            for i in outputs:
                i = i.strip(',;')
                p = re.compile(r"\[.*\]")
                i = p.sub('', i)
                pri_outs.append(i)

        if state.split()[0] not in ["module", "input", "output", "wire"]:
            # print "*", state, "*"
            
            dev_type = state.split()[0]
            
            # some pins are like ume[0], ume[1]
            # change them into ume_0, ume_1
            all_array = re.findall(r'\[.*?\]', state)
            
            for a in all_array:
                state = state.replace(a, "_b%sb" % a.strip('[]'))
                
            state = state.replace('\\', '')
            
            if device.has_key(dev_type):
                device[dev_type] += 1
            else:
                device[dev_type] = 1
            
            a1 = state.split()[1]
            
            # get device name
            if '(' not in a1:
                device_name = a1.strip()
            else:                
                s = re.search(r"(.*?)[ ]?\(", a1)
                        
                if s is None or len(s.groups())==0 or s.groups()[0]=='':
                    print "Error!! No dev name in %s" % state
                    device_name = "no_name"
                else:                                                    
                    device_name = s.groups()[0]            
            
            # generate device : state
            if device_name != "no_name":
                dev_state[device_name] = state
                type_dict[device_name] = dev_type
            
            #if device_name == "NAND2X1":
            #    print a1
            
            tin = []
            tout = "no_output"

            if dev_type=='assign':
                pin = state.split()[1]
                assigns[pin] = state
                # print assigns
            
            # get output and inputs of the devices

            # if the module is not DFF
            # then .Y indicates the output
            if dev_type not in ['DFFSRX1', 'SDFFSRX1', 'DFFX1', 'assign']:                
                pattern = r".Y ?\((.*?)\)"
                
                if dev_type == 'ADDHX1':
                    pattern = r".S ?\((.*?)\)"
                    
                s = re.search(pattern, state)
                
                if s is None or len(s.groups())==0:
                    print "Error!! No output in %s" % state
                    
                else:
                    tout = s.groups()[0]
                    
                dev_clk[device_name] = "null"

            elif dev_type in ['DFFX1', 'DFFSRX1', 'SDFFSRX1']:
                
                dffs_list.append(device_name)
                
                # get the clock
                pattern = r"CK[ ]?\(([^ ]*?)[ ]?\)"
                clk = re.findall(pattern, state)
                
                if len(clk) == 0 or len(clk[0].strip())==0:
                    print "Error!! no clk in %s" % state
                else:
                    clk = clk[0].strip()
                
                if clk_dff.has_key(clk):
                    clk_dff[clk].append(device_name)
                else:
                    clk_dff[clk] = [device_name]                        
                
                dev_clk[device_name] = clk
                
                pattern = r"Q[N]? ?\(([^ ]*?) ?\)"
                s = re.findall(pattern, state)
                l = reduce(lambda x,y: len(x)+len(y), s)
                if l == 0 or len(s) > 2:
                    print "Error!! no output found in %s" % state
                    
                else:
                    # has more than one output
                    if len(s[0])>0 and len(s[1])>0:
                        print "more than one output in", state
                        print "the outputs are", s                    
                    try:
                        tout = len(s[0]) > 0 and s[0] or s[1]
                        #print "tout is %s in %s" % (tout, state)
                    except IndexError:
                        print "****", s, state
            
            # if output is already in out_dict
            if out_dict.has_key(tout):
                print "Error!! %s already in out_dict" % tout
                print "And it is %s" % out_dict[tout]
            else:                                                                    
                out_dict[tout] = device_name

            
            if device_name != "no_name":
                dev_out[device_name] = tout
            
            # get all input pins using regex
            tin_port = []
            input_pins = ['A', 'B', 'C', 'D', 'A0', 'A1', 'B0', 'B1', 'C0', 'S0']            
            for i in input_pins:
                pattern = r"%s ?\((.*?)\)" % i
                str = get_by_regex(pattern, state)
                if str is not None and str.strip() != tout:
                    tin.append(str.strip())
                    tin_port.append(i)

            
            if device_name != "no_name":
                dev_in[device_name] = tin
                dev_in_port[device_name] = tin_port

            j = 0
            for i in tin:
                if not in_dict.has_key(i):
                    in_dict[i] = [device_name]
                    in_dict_port[i] = [tin_port[j]]
                else:
                    in_dict[i].append(device_name)                                
                    in_dict_port[i].append(tin_port[j])                
                j += 1

            #if device_name == "g40434":
            #    print "dev_in", dev_in[device_name]
            #    print "in_dict", in_dict['n_1083']
            
        state = ""
    
#    for dev in dev_clk:
#        if dev_clk[dev] == "null":
#            path = [dev]
#            
#            next = in_dict[dev_out[dev]]
#            while (dev_clk[next] == "null"):
#                path.append(next)
#                next = dev_out[dev]
            
            
        #print "*%s*" % key, dff_clk[key]
                
    for key in clk_dff:
        pass
        #print "*%s*" % key, clk_dff[key]
    
    for key in dev_out.keys():
        pass
        #print "*%s*" % key, dev_out[key]
    
    for key in in_dict.keys():
        pass
        #print "*%s*" % key, in_dict[key]    
    
    for key in out_dict.keys():
        pass
        #print "*%s*" % key, out_dict[key]

    #print "@@@@@", out_dict['n_7155']
    
    for key in device.keys():
        pass
        #print key, device[key]


    #print "*******************"
    #print dev_out['g29896']
    #print dev_in['g29896']
    #print dev_in_port['g29896']
    #print dev_out['u1_slt2_reg_b19_b']
    #print dev_in['u1_slt2_reg_b19_b']
    #print dev_in_port['u1_slt2_reg_b19_b']
    #print "*******************"
    #

    def get_touched(out, l):
        '''
        '''
        if out in in_dict.keys():
            for dev in in_dict.keys():
                if dev in dffs_list:
                    continue
                # not dff, add to the list if it is not already in it
                if dev in l:
                    continue
                l.append(dev)
                # traverse each of dev's outputs to continue this process
                if dev in dev_out.keys():
                    for o in dev_out[dev]:
                        get_touched(o, l)

    # process each primary inputs to get all combinational gates which could be directly touched by them
    # by 'directly' we mean no DFF on the path
    #pri_touch = {}
    #for pri_in in pri_ins:
    #    pri_touch[pri_in] = []
    #    get_touched(pri_in, pri_touch[pri_in])
    #    print pri_in, len(pri_touch[pri_in])
    # print in_dict['in_slt_845']

        
    # traverse the DFF in every single clock domain 
    # to find DFFs at clock boundary
    paths = {}
    
    def get_recv_dff(out, clk, origin, paths, path):        
        '''
        get a list of DFFs which could be reached from out
        @parameters:
            out: output pin
            clk: which clock domain this belongs to
            origin: origin where the traversal begins
            paths: a dictionary. key is the start and the end of the path, both of which are dffs, value is the path.
            path: current path, when it ends with a dff, it will be added into paths

        @brief:
            This is implemented by recursion
        '''
        #print "called by out:%s, origin:%s, path:%s" % (out, origin, path)
        if out is None:
            #print "[Debug] out %s of %s is none" % (out, origin)
            return []
                
        recv_dff = set([])
        
        if out not in in_dict.keys():
            #print "[Debug] out %s of %s connects nothing" % (out, origin)
            return recv_dff
        
        path_base = path
        # traverse every dev which is attached to output of current device
        for next_dev in in_dict[out]:
            path = path_base + ("-" + next_dev)
            if next_dev in dffs_list:
                # print "[in] %s => %s" % (origin, next_dev)
                recv_dff.add(next_dev)
                paths["%s-%s" % (origin, next_dev)] = path
            else: # is a normal device
                out = dev_out[next_dev]
                
                if next_dev not in dev_clk.keys():
                    dev_clk[next_dev] = clk
                    dev_origin[next_dev] = origin
                elif dev_clk[next_dev] != clk:
                    pass
                    #print "Error!! Inconsistent clk for device %s" % next_dev
                    #print "    %s (from %s) != %s (from %s)" % (dev_clk[next_dev], dev_origin[next_dev], clk, origin)
                    
                # out is primary output and connectes to nothing
                if out not in in_dict.keys():
                    continue
                
                recv_dff = recv_dff.union(get_recv_dff(out, clk, origin, paths, path))
                
        return recv_dff

    # print get_recv_dff(dev_out['u1_slt2_reg_b19_b'], dev_clk['u1_slt2_reg_b19_b'], 'u1_slt2_reg_b19_b', paths, 'u1_slt2_reg_b19_b')
    # print paths
    
    for clk in clk_dff:
        #print "Processing DFFs in clock %s" % clk
        for dff in clk_dff[clk]:
            
            out = dev_out[dff]        
            
            recv_dff = get_recv_dff(out, clk, dff, paths, dff)
            # print "*%s*" % dff, recv_dff
                                                                                              
            for r in recv_dff:                                                                
                if dev_clk[r] != dev_clk[dff]:                                                
                    # print "[CB] %s .CK(%s) => %s .CK(%s)" % (dff, dev_clk[dff], r, dev_clk[r])
                    # print "  ", paths['%s-%s' % (dff, r)]
                    out = dev_out[r]
                    
                    if out in in_dict.keys():
                        # r_next is the successor of r
                        # r_next_port is the port connecting r and r_next
                        # we need to get this because fastscan cannot get pattern for fault at DFF's out
                        # but if we set the fault as the input of the successor
                        # which we think is equiavalent to the output of the dFF
                        # we could get the pattern
                        flag = True
                        for i in xrange(len(in_dict[out])):
                            if in_dict[out][i] not in dffs_list:
                                r_next = in_dict[out][i]
                                r_next_port = in_dict_port[out][i]
                                flag = False
                                break
                        
                        if not flag: # a non-DFF device is found as successor of r
                            succ_dev[r] = r_next 
                            succ_port[r] = r_next_port

                        ck_bound.append((dev_clk[dff], dev_clk[r], dff, r, paths['%s-%s' %(dff, r)]))                                   

    def assign_clk(out, clk):
        if out in out_dict.keys():
            dev = out_dict[out]
            if dev_clk[dev] == "null":
                dev_clk[dev] = clk
                try:
                    for i in dev_in[dev]:
                        assign_clk(i, clk)                        
                except KeyError:
                    print "Error!! dev %s is not in dev_in.keys()" % dev
                    
    
    # reverse tracking from dff to determine clock domain of each gate
    for clk in clk_dff.keys():
        for dff in clk_dff[clk]:
            try:
                for i in dev_in[dff]:
                    assign_clk(i, clk)
            except KeyError:
                print "KeyError", dev_state[dff]
    
    # there is a bug here
    #print "======", dev_clk['g41347']
    for dev in dev_clk.keys():
        if dev_clk[dev] == "null":
            print dev, "null"

    # output the original netlist, with only scan-chain added
    f = open("new.v", "w+")
    # we need write input, wire, output, and devices, and scan chain

    new_pri_outs = Set([])
    new_pri_ins = Set([])
    new_wires = Set([])

    temp_pri_ins = pri_ins[:]
    temp_pri_outs = pri_outs[:]

    # process the clocks
    for clk in clk_dff.keys():
        if clk in pri_ins:
            new_pri_ins.add(clk)
            if clk in temp_pri_ins:
                temp_pri_ins.remove(clk)
        elif clk in pri_outs:
            new_pri_outs.add(clk)
        else:
            new_wires.add(clk)

    for dev in dev_state.keys():
        #print dev_state[dev]

        # check if its output is primary output
        temp_out = dev_out[dev]
        flag_out = False
        if temp_out in pri_outs:
            new_pri_outs.add(temp_out)
            flag_out = True
            if temp_out in temp_pri_outs:
                temp_pri_outs.remove(temp_out)
        else:
            # sometimes, abc[1] will be converted into abc_b1b
            p = re.compile(r"_b\d+b$")
            if len(p.findall(temp_out)) > 0:
                temp_temp_out = p.sub('',temp_out)
                if temp_temp_out in pri_outs:
                    new_pri_outs.add(temp_out)
                    flag_out = True
                    if temp_temp_out in temp_pri_outs:
                        temp_pri_outs.remove(temp_temp_out)
        if not flag_out:
            new_wires.add(temp_out)            

        for temp_in in dev_in[dev]:
            flag_in = False
            if temp_in in pri_ins:
                flag_in = True
                new_pri_ins.add(temp_in)
                if temp_in in temp_pri_ins:
                    temp_pri_ins.remove(temp_in)
            else:
                # sometimes, abc[1] will be converted into abc_b1b
                p = re.compile(r"_b\d+b$")
                if len(p.findall(temp_in)) > 0:
                    temp_temp_in = p.sub('',temp_in)
                    if temp_temp_in in pri_ins:
                        new_pri_ins.add(temp_in)
                        flag_in = True
                        if temp_temp_in in temp_pri_ins:
                            temp_pri_ins.remove(temp_temp_in)
            if not flag_in:
                new_wires.add(temp_in)

    print "temp", temp_pri_ins
    print "temp", temp_pri_outs
    for i in temp_pri_ins:
        new_pri_ins.add(i)
    for o in temp_pri_outs:
        new_pri_outs.add(o)
            
    # generate scan-chain
    #  model SDFFN (CK, D, Q, SO, RT, ST, SE, SI)
    #  model SDFFNSRN (CK, D, Q, SO, SE, S*)
    # 
    #  DFFX1 u9_empty_reg(.CK (clk_i), .D (n_5613), .Q (), .QN (i3_empty));
    #  => SDFFNSR u9_empty_reg(.CK(clk_i), .D(n_5163), .Q(i3_empty), .SE(scan_enable), SI(last_output))
    #
    scan_chain = []
    
    last_output = "scan_data_in";
    for clk in clk_dff.keys():
        for dff in clk_dff[clk]:
            state = dev_state[dff]
            dev_type = state.split()[0]
            
            pattern_base = r"%s ?\((.*?)\)"
            
            input = dev_in[dff][0]
            output = dev_out[dff]            
            
            if dev_type == "DFFX1":                
                new_dff = "SDFFNSRN %s (.CK(%s), .D(%s), .Q(%s), .SO(%s), .SE(scan_enable), .SI(%s));" % \
                                  (dff, clk, input, output, output, last_output)
                
                
                # get input
            elif dev_type == "DFFSRX1":
            #  DFFSRX1 valid_s_reg(.RN (1'b1), .SN (1'b1), .CK (clk_i), .D(valid_s1), .Q (valid_s), .QN ());
            #  => SDFF valid_s_reg(.RT (), .ST(), .CK(), .D, .Q)
                
                RN = ""
                pattern = pattern_base % "RN"
                str = get_by_regex(pattern, state)
                if str is not None:
                    RN = str
                    
                SN = ""
                pattern = pattern_base % "SN"
                str = get_by_regex(pattern, state)
                if str is not None:
                    SN = str
                    
                new_dff = "SDFFN %s (.CK(%s), .D(%s), .Q(%s), .SO(%s), .RT(1'b0), .ST(1'b0), .SE(scan_enable), .SI(%s));" % \
                            (dff, clk, input, output, output, last_output)
                    
            last_output = output
            scan_chain.append(new_dff)
            
    
    # print "Inputs ", new_pri_ins
    # print "Outputs ", new_pri_outs

    f.write('''
module buf1 (out, in);
output out;
input in;
buf (out, in);
endmodule
''')
    
    f.write("module new_module (")
    
    f.write("scan_enable, scan_data_in, scan_data_out, ")

    # initialize the type of assign pins
    # {pin_name: type} and type is [input, output, wire]
    apin_type = {}

    #print "new_pri_ins", new_pri_ins

    all_pins = Set([])
    for i in new_pri_ins:
        all_pins.add(i)
        if i in assigns.keys():
            apin_type[i] = "input"
    for i in new_pri_outs:
        all_pins.add(i)
        if i in assigns.keys():
            apin_type[i] = "output"

    l = 0
    for i in all_pins:
        f.write(i)
        l += 1
        if l != len(all_pins):
            f.write(", ")

    f.write(");\n\n")
    
    f.write( "input scan_enable, scan_data_in" )
    for i in new_pri_ins:
        f.write(", ")
        f.write(i)
    f.write(";\n")
    
    f.write("output scan_data_out")        
    for o in new_pri_outs:
        f.write(", ")
        f.write(o)
    f.write(";\n")
    
    for w in new_wires:
        if i in assigns.keys():
            apin_type[i] = "wire"
        f.write("wire %s;\n" % w)
    
    # f.write("wire ")
    # if clk in wires_by_clk.keys():
    #     for w in range(len(wires_by_clk[clk])):
    #         if w != 0:
    #             f.write(", ")
    #         f.write(wires_by_clk[clk][w])
    # f.write(";\n")

    # output the assign statement
    # we've already store the type of the pin in apin_type
    for apin in assigns.keys():
        if apin not in apin_type.keys():
            f.write("// add wire for assign statement\n")
            f.write("wire %s;\n" % apin)
        f.write(assigns[apin] + '\n')
    
    # output the scan chain
    f.write("// scan chain begins here\n")
    for dff in scan_chain:
        f.write(dff + "\n")        
    f.write("// scan chain ends here\n")
    
    f.write("\n buf1 BUFbread(scan_data_out, %s);\n" % last_output)
    
    for dev in dev_state.keys():
        f.write(dev_state[dev] + "\n")
            
    f.write("\nendmodule")
        
    f.close()

    # output all DFFs in clk_i domain and in clock boundaries
    # to check if its input are from primary inputs
    # in oder to check this, we tarverset each pair in ck_boundary
    # for every pair, there is "from_dff => combinational logic => to_dff"
    # we check each input of each combinational gate on the path
    # if one of it is directly from primary input, which means, 
    # without DFF on its way from primary input
    # we need to add extra control to the inputs to make sure that the fault is from the sender domain
    # the extra control is added by generating constraints using another script parse_path.py
    # we need only output the path, including detailed information here
    for cb in ck_bound:
        (from_clk, to_clk, from_dff, to_dff, path) = cb
        # print to_clk, RECV_DOMAIN
        if to_clk == RECV_DOMAIN:
            path = path.split('-')
            # print "path", path

            send_dff = path[0]

            try:
                send_dff_in = dev_in[send_dff][0]
                # this is the gate before DFF in sender domain
                # we need this because we need to add faults here instead of input of the DFF
                # otherwise the pattern could not be generated
                b4_send = out_dict[send_dff_in] 
            #print b4_send
            except KeyError:
                b4_send = None 
                print 'pi',

            # if b4_send is DFF
            if b4_send in dffs_list:
                print "DFF %s:Q(%s) -- " % (b4_send, dev_out[b4_send]), 
            else:
                print "%s:Y(%s) -- " % (b4_send, dev_out[b4_send]), 
            
            print "%s[%s]" % (send_dff,dev_clk[send_dff]),  "===>", 

            # for every gate on the path, we need the gate type, pin name, pin name in definition
            # gate type and pin name in definition is used to determine which constraint to add
            # also, pin name in definition is used to add the constraint into dofile
            out = dev_out[path[0]]
            for i in xrange(1, len(path)-1):
                print path[i], 
                index = 0
                while True:
                    if index >= len(dev_in[path[i]]):
                        break
                    if dev_in[path[i]][index] == out:
                        if out in new_pri_ins:
                            print "[%s @ %s]:%s(pi:%s)" % (type_dict[path[i]], dev_clk[path[i]], dev_in_port[path[i]][index], out),
                        else:
                            print "[%s @ %s]:%s(%s)" % (type_dict[path[i]], dev_clk[path[i]], dev_in_port[path[i]][index], out),
                        break
                    index += 1

                print "===>", 
                out = dev_out[path[i]]

            recv_dff = path[-1]

            print "%s[%s](%s)" % (recv_dff, dev_clk[recv_dff], out), 

            # Also, we need combinational logic gate immediately after the DFF in order to inject fault
            if recv_dff in succ_dev.keys():
                print "-- %s:%s" % (succ_dev[recv_dff], succ_port[recv_dff])
            else:
                print "-- DFF"
            
            

if __name__ == '__main__':
    process()

#        # if the statements startswith "input", "output", "wire"
#        # we need to output them immediately
#        if elements[0] in ["input", "output", "wire"]:
#            
#            fout.write("%s %s\n" % (elements[0], gen_pins(elements[1], "send")))
#            fout.write("%s %s\n" % (elements[0], gen_pins(elements[1], "recv")))            
#        else:
