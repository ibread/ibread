#!/usr/bin/python

# Problems:
#   1. after splitting, need to reparse to get primary inputs and ouptuts
#        some inputs are arrays, such as " input a[3]"
#       not sure if "input a[0], a[1], a[2]" works or not
#   2. some gates attach to none DFFs, do not know how to assign clocks to them
# 


import os, sys, re

if len(sys.argv) < 2:
    print "Usages: %s FILENAME" % sys.argv[0]
    sys.exit(1)

source = sys.argv[1]

class node:
    name = "default"
    input = []
    output = []
    
    def __init__(self, name, input, output):
        self.name = name
        self.input = input
        self.output = output
        
class DFF:
    def __init__(self, d, q, qn, clk):
        self.d = d
        self.q = q
        self.qn = qn
        self.clk = clk

def pre_process():
    
    filename = "ac97_ctrl.v"
    try:
        fin = open(filename, "r")
    except IOError:
        print "Error openning %s" % filename
        sys.exit(1)
        
    in_dict = {}
    out_dict = {}
    
    
    statement = ""
    
    for line in fin:
        line = line.strip()
        
        if line.startswith('//'):
            continue


def generate():
    
    try:
        fin = open(source)
    except IOError:
        print "Error openning %s, plz check it out." % source

    dest = "%s_cdc.v" % os.path.splitext(source)[0]
    try:
        fout = open(dest, "w+")
    except IOError:
        print "Error openning %s, plz check it out." % dest

    # This indicates the start of module
    indicator = False

    statement = ""

    # primary input
    pi = []
    # primary output
    po = []
    # wires
    wire = []
    # dffs
    dffs = []
    # all statements
    all_statements = []
    
    for line in fin:
        if line.count("module") > 0:
            indicator = True
    
        # Do nothing if we're outside of module or encountering comments
        if (not indicator) or line.strip().startswith("//"):
            fout.write(line)
            continue

        if indicator and line.count("endmodule") > 0:
            indicator = False
            
        statement += line.strip()
    
        # if no ";", this statement is not completed
        if line.count(";") == 0:
            continue

        #print statement
    
        elements = statement.split(" ", 1)
        
        # parse primary input
        if elements[0] == "module":
            module = elements[1].strip(';').split('(')[0]
        elif elements[0] == "input":
            pi.extend(elements[1].strip(';').split(',')) 
        elif elements[0] == "output":
            po.extend(elements[1].strip(';').split(','))
        elif elements[0] == "wire":
            wire.extend(elements[1].strip(';').split(','))
        elif elements[0] == "dff":
            dffs.append(elements[1].strip(';'))
        else:
            all_statements.append(statement)
            
        # initialize statement for next round 
        statement = ""

    # remove some useless inputs
    for s in ["CK", "GND", "VDD"]:
        if s in pi:
            pi.remove(s)
    
    # add dffs at the start & the end of the circuits
    # input: i1 => dff(CK, i1, ii1)
    # output: o1 => dff(CK, oo1, o1)
    #
    # Note that since we merge two copies of the same benchmark together
    # We could not just insert DFFs at the head and rear, and then double them
    # DFFs at the rear of Sender domain and the head of the Receiver Domain
    # needs to be connected together
    #
    # All added DFFs are at mid_dffs
    mid_dffs = []
    si = len(pi)
    so = len(po)
    added_pi = []
    added_po = []

    # Additional DFFs are added into inputs and outputs of Receiver Domain
    # Additional DFFs are added only into inputs of Sender Domain
    # This is because we need to connect outputs of Sender Domain into inputs of Receiver Domain
    # This is done by DFFs added into outputs of Sender Domain, which is done later
    for i in xrange(len(pi)):
        # these are not primary inputs
        if pi[i] in ["CK", "GND", "VDD"]:
            continue
        mid_dffs.append("SEND_I_DFF%d(send_CK, send_%s, hsend_%s)" % (i, pi[i], pi[i]))
        mid_dffs.append("RECV_I_DFF%d(recv_CK, recv_%s, hrecv_%s)" % (i, pi[i], pi[i]))
        added_pi.append("hsend_%s" % pi[i])
        
    for i in xrange(len(po)):
        mid_dffs.append("RECV_O_DFF%d(recv_CK, hrecv_%s, recv_%s)" % (i, po[i], po[i]))
        added_po.append("hrecv_%s" % po[i])

    # Connect Sender Domain to Receiver Domain with DFFs at the output of Sender Domain
    # more inputs than outputs, which means inputs left to be primary inputs
    if si >= so:
        for i in xrange(si):
            if i < so:
                mid_dffs.append("MID_DFF%d(send_CK, hrecv_%s, hsend_%s)" % (i, pi[i], po[i]))
            else:
                added_pi.append("hrecv_%s" % pi[i])
    else: # si < so
        for i in xrange(so):
            if i < si:
                mid_dffs.append("MID_DFF%d(send_CK, RECV_%s, SEND_%s)" % (i, "H"+pi[i], po[i]))
            else:
                # add additional DFFs at the output of Sender Domain because these outputs will be
                # used as primary output
                mid_dffs.append("SEND_O_DFF%d(send_CK, hsend_%s, send_%s)" % (i, po[i], po[i]))
                added_po.append("hsend_%s" % po[i])

    # output module
    # module s27 (CK, GND, ...)
    #
    # inputs include 3 parts: send_ + pi, recv_ + pi, added_pi
    # so do outputs
    inputs = "scan_enable, scan_data_in, send_CK, send_GND, send_VDD, recv_CK, recv_GND, recv_VDD, " + ', '.join(added_pi)
    outputs = 'scan_data_out, ' + ', '.join(added_po)
    wires = "%s, %s, %s, %s, %s, %s" % (gen_pins(pi, "send"), gen_pins(pi, "recv"),
                                        gen_pins(po, 'send'), gen_pins(po, "recv"),
                                        gen_pins(wire, 'send'), gen_pins(wire, 'recv') )
    

    fout.write("module %s (%s, %s);\n\n" % (module, inputs, outputs))

    #output input, wire, output
    fout.write("input %s;\n\n" % inputs)
    fout.write("wire %s;\n\n" % wires)
    fout.write("output %s;\n\n" % outputs)
    
    # output DFF and connect the scan chain
    fout.write("\n// scan chain begins here\n\n")

    last_input = "scan_data_in"

    print mid_dffs

    mid_dffs = sorted(mid_dffs, key=lambda x:x[0]=='S' and 'O' or x[0])
    
    for md in mid_dffs:
        (instance, pins) = md.split('(')
        pins = map(lambda x: x.strip(), pins.rstrip(');').split(','))
        
        fout.write("SDFFNSR %s(.CK(%s), .D(%s), .Q(%s), .SI(%s), .SE(scan_enable));\n" %
                   (instance, pins[0], pins[2], pins[1], last_input))
        last_input = pins[1]
    
    fout.write("// All orignal DFFs are extended into 2 copies\n")

    for i in xrange(2):
        if i == 0:
            t = "send_"
        else:
            t = "recv_"

        for d in dffs:
            (instance, pins) = d.split('(')
            pins = map(lambda x: x.strip(), pins.rstrip(');').split(','))
            fout.write("SDFFNSR %s%s (.CK(%s), .D(%s), .Q(%s), .SI(%s), .SE(%s));\n" %
                                (t.swapcase(), instance, t+pins[0], t+pins[2], t+pins[1],
                                 last_input, "scan_enable"))
            
            last_input = t + pins[1]
    fout.write("//END: All orignal DFFs are extended into 2 copies")

    
    fout.write("// scan chain ends here\n\n")
    fout.write("buf1 BUF(scan_data_out, %s);\n\n" % last_input)
    
    
    # output all other statement
    for state in all_statements:
        # dff DFF_0(CK,G5,G10);
        elements = state.split(' ', 1)
        module = elements[0] #dff 
        (instance, pins) = elements[1].split('(') #DFF_0
        pins = map(lambda x:x.strip(), pins.rstrip(');').split(',')) # CK,G5,G10
        
        fout.write("%s SEND_%s(%s);\n" % (module, instance, gen_pins(pins, "send")))
        fout.write("%s RECV_%s(%s);\n" % (module, instance, gen_pins(pins, "recv")))        


    fout.write("endmodule\n")

    fout.write('''
module buf1 (out, in);
    output out;
    input in;
    buf (out, in);
endmodule
    \n\n''')
    fout.write("//# %d DFFs" % (len(mid_dffs) + 2*len(dffs)))

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

def get_by_regex(pattern, string):
    '''
    Given a pattern and string, return the result by regex matching
    '''
    
    s = re.findall(pattern, string)
    
    if len(s) == 0:
        return None
    else:
        return s[0]

def process():
    try:
        fin = open(source)
    except IOError:
        print "Error openning %s, plz check it out." % source
        
    inside = False
    state = ""
    # device_type:device_number
    device = {}
    
    # output lookup table, output : device_name
    out_dict = {}
    
    #input lookup table, input: device_name
    in_dict = {}
    
    # device_name:output
    dev_out = {}
    # device_name: list(input)
    dev_in = {}
    
    # clk: list(dff)
    clk_dff = {}
    
    # for every dff, there is a clock attached
    # for other device, the clock is assigned by the one of the dff which 
    # is upstream of it
    dev_clk = {} # dev:clk
    dev_state = {} # dev:statement
    
    # each time a device is assigned a clock
    # there must be a dff driving it, which is called as origin
    dev_origin = {}
    
    # list( (send_clk, send_dff, recv_dff) )
    ck_bound = []
    # list(dff)
    dffs_list = []


    for line in fin:
        
        if line.startswith("module"):
            inside = True
        elif line.startswith("endmodule"):
            inside = False
        
        # skip comments
        if not line or line.startswith('//'):
            continue
    
        state += line.strip()
        
        if not state.endswith(';'):
            continue
                
        if state.split()[0] not in ["module", "input", "output", "wire"]:
            #print "*", state, "*"
            
            dev_type = state.split()[0]
            
            # some pins are like ume[0], ume[1]
            # change them into ume_0, ume_1
            all_array = re.findall(r'\[.*?\]', state)
            
            for a in all_array:
                state = state.replace(a, "_b%s_b" % a.strip('[]'))
                
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
            
            if device_name == "NAND2X1":
                print a1
            
            tin = []
            tout = "no_output"
            
            # get output and inputs of the devices
            
            # if the module is not DFF
            # then .Y indicates the output
            if dev_type not in ['DFFSRX1', 'DFFX1', 'assign']:                
                pattern = r".Y ?\((.*?)\)"
                
                if dev_type == 'ADDHX1':
                    pattern = r".S ?\((.*?)\)"
                    
                s = re.search(pattern, state)
                
                if s is None or len(s.groups())==0:
                    print "Error!! No output in %s" % state
                    
                else:
                    tout = s.groups()[0]
                    
                dev_clk[device_name] = "null"

            elif dev_type in ['DFFX1', 'DFFSRX1']:
                
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
            input_pins = ['A', 'B', 'C', 'D', 'A0', 'A1', 'B0', 'B1', 'C0', 'S0']            
            for i in input_pins:
                pattern = r"%s ?\((.*?)\)" % i
                str = get_by_regex(pattern, state)
                if str is not None and str.strip() != tout:
                    tin.append(str.strip())

            
            if device_name != "no_name":
                dev_in[device_name] = tin
            
            for i in tin:
                if not in_dict.has_key(i):
                    in_dict[i] = [device_name]
                else:
                    in_dict[i].append(device_name)                                

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
    
    for key in device.keys():
        pass
        #print key, device[key]
        
    # traverse the DFF in every single clock domain 
    # to find DFFs at clock boundary
    
    def get_recv_dff(out, clk, origin):        
        '''
        get a list of DFFs which could be reached from out and with different clock from "clk"
        '''
        if out is None:
            return []
                
        recv_dff = []
        
        if out not in in_dict.keys():
            return []
        
        # traverse every dev which is attached to output of current device
        for next_dev in in_dict[out]:
            if next_dev in dffs_list:
                recv_dff.append(next_dev)
            else: # is a normal device
                out = dev_out[next_dev]
                
                if next_dev not in dev_clk.keys():
                    dev_clk[next_dev] = clk
                    dev_origin[next_dev] = origin
                elif dev_clk[next_dev] != clk:
                    #print "Error!! Inconsistent clk for device %s" % next_dev
                    #print "    %s (from %s) != %s (from %s)" % (dev_clk[next_dev], dev_origin[next_dev], clk, origin)
                    continue
                    
                if out not in in_dict.keys():
                    return []
                
                recv_dff.extend(get_recv_dff(out, clk, origin))
                
        return recv_dff
    
    for clk in clk_dff:
        for dff in clk_dff[clk]:
            out = dev_out[dff]        
            recv_dff = get_recv_dff(out, clk, dff)
            #print "*%s*" % dff, recv_dff
            
            for r in recv_dff:
                if dev_clk[r] != dev_clk[dff]:
                    #print "[CB] %s .CK(%s) => %s .CK(%s)" % (dff, dev_clk[dff], r, dev_clk[r])
                    ck_bound.append((dev_clk[dff], dff, r))


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
    
    # when we split the circuits, we need to redefine the input and output
    inputs_by_clk = {}
    outputs_by_clk = {}
    wires_by_clk = {}
    
    # these is a bug here
    #print "======", dev_clk['g41347']
    for dev in dev_clk.keys():
        if dev_clk[dev] == "null":
            print dev, "null"


    
    for clk in clk_dff:
        print "===================%s begins===================" % clk
        
        f = open("%s.v" % clk, "w+")
        
        
        for dev in dev_clk:
            if dev_clk[dev] == clk:
                
                is_pri_out = True
                # check if its output is primary 
                if dev_out[dev] in in_dict.keys(): # check all devices connected to its output
                    for next in in_dict[dev_out[dev]]:
                        # if there is one sucessor device in the same clock domain
                        # then dev's output is not primary output
                        if dev_clk[next] == dev_clk[dev]: 
                            is_pri_out = False
                            break
                temp_out = dev_out[dev]
                if is_pri_out:
                    if clk in outputs_by_clk.keys():
                        if temp_out not in outputs_by_clk[clk]:
                            try:
                                outputs_by_clk[clk].append(temp_out)
                            except KeyError:
                                print "KeyError", clk, dev
                    else:
                        try:
                            outputs_by_clk[clk]= []
                        except KeyError:
                            print "KeyError", clk, dev
                else:
                    if clk in wires_by_clk.keys():
                        if temp_out not in wires_by_clk[clk]:                            
                            wires_by_clk[clk].append(dev_out[dev])
                    else:
                        wires_by_clk[clk] = [dev_out[dev]]
                # check if its inputs are primary
                
                
                for i in dev_in[dev]:    
                    
                    is_pri_in = True                
                    if i in out_dict.keys() and dev_clk[out_dict[i]] == clk:
                        is_pri_in = False
                    
                    if is_pri_in:
                        if clk in inputs_by_clk.keys():
                            if i not in inputs_by_clk[clk]:
                                inputs_by_clk[clk].append(i)
                        else:
                            inputs_by_clk[clk] = [i]
                    else:
                        if clk in wires_by_clk.keys():
                            if i not in wires_by_clk[clk]:
                                wires_by_clk[clk].append(i)
                        else:
                            wires_by_clk[clk] = [i]
                
                #f.write(dev_state[dev] + "\n")
        
        # generate scan-chain
        #  model SDFF (D, SI, SE, ST, RT, CK, Q) 
        #  model SDFFNSR (D, SI, SE, CK, Q) 
        # 
        #  DFFX1 u9_empty_reg(.CK (clk_i), .D (n_5613), .Q (), .QN (i3_empty));
        #  => SDFFNSR u9_empty_reg(.CK(clk_i), .D(n_5163), .Q(i3_empty), .SE(scan_enable), SI(last_output))
        #

        
        scan_chain = []
        
        last_output = "scan_data_in";
        for dff in clk_dff[clk]:
            state = dev_state[dff]
            dev_type = state.split()[0]
            
            pattern_base = r"%s ?\((.*?)\)"
            
            input = dev_in[dff][0]
            output = dev_out[dff]            
            
            if dev_type == "DFFX1":
                
                new_dff = "SDFFNSR %s (.CK(%s), .D(%s), .Q(%s), .SE(scan_enable), .SI(%s))" % \
                                  (dff, clk, input, output, last_output)
                
                
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
                    
                new_dff = "SDFF %s (.CK(%s), .D(%s), .Q(%s), .RT(%s), .ST(%s), .SE(scan_enable), .SI(%s))" % \
                            (dff, clk, input, output, RN, SN, last_output)
                    
            last_output = output
            scan_chain.append(new_dff)
            
    
        f.write('''
    module buf1 (out, in);
        output out;
        input in;
        buf (out, in);
    endmodule
    ''')
    
    
        
        f.write("module %s_domain (" % clk)
        
        f.write("scan_data_in, scan_data_out, %s, " % clk)
        
        for i in inputs_by_clk[clk]:
            f.write(i + ", ")
            
        for i in xrange(len(outputs_by_clk[clk])):
            f.write(outputs_by_clk[clk][i])            
            if i != len(outputs_by_clk[clk])-1:
                f.write(", ")
        
        f.write(");\n\n")
        
        f.write( "input scan_data_in, %s, " % clk) 
        if clk in inputs_by_clk.keys():
            for i in xrange(len(inputs_by_clk[clk])):
                if i != 0:
                    f.write(", ")
                f.write(inputs_by_clk[clk][i])
        f.write(";\n")
        
        f.write("output scan_data_out, ")        
        if clk in outputs_by_clk.keys():
            for o in xrange(len(outputs_by_clk[clk])):
                if o != 0:
                    f.write(", ")
                f.write(outputs_by_clk[clk][o])
        f.write(";\n")
        
        if clk in wires_by_clk.keys():
            for w in wires_by_clk[clk]:
                f.write("wire %s;\n" % w)
        
#        f.write("wire ")
#        if clk in wires_by_clk.keys():
#            for w in range(len(wires_by_clk[clk])):
#                if w != 0:
#                    f.write(", ")
#                f.write(wires_by_clk[clk][w])
#        f.write(";\n")
#        
        f.write("\n buf1 BUFbread(scan_data_out, %s);\n" % last_output)
        
        for dff in scan_chain:
            f.write(dff + "\n")        
        
        for dev in dev_clk.keys():
            if dev_clk[dev] == clk and dev not in clk_dff[clk]:                
                f.write(dev_state[dev] + "\n")
                
        f.write("\nendmodule")
            
        f.close()
        print "===================%s ends===================" % clk
            

if __name__ == '__main__':
    process()

#        # if the statements startswith "input", "output", "wire"
#        # we need to output them immediately
#        if elements[0] in ["input", "output", "wire"]:
#            
#            fout.write("%s %s\n" % (elements[0], gen_pins(elements[1], "send")))
#            fout.write("%s %s\n" % (elements[0], gen_pins(elements[1], "recv")))            
#        else:
