#!/usr/bin/python

import os, sys

if len(sys.argv) < 2:
    print "Usages: %s FILENAME" % sys.argv[0]
    sys.exit(1)

source = sys.argv[1]

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


def main():
    """main function"""


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
        if line.count("module s27") > 0:
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
            print elements[1]
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
                added_po.append("send_%s" % po[i])

    # output module
    # module s27 (CK, GND, ...)
    #
    # inputs include 3 parts: send_ + pi, recv_ + pi, added_pi
    # so do outputs
    inputs = "send_CK, send_GND, send_VDD, recv_CK, recv_GND, recv_VDD, " + ', '.join(added_pi)
    outputs = ', '.join(added_po)
    wires = "%s, %s, %s, %s, %s, %s" % (gen_pins(pi, "send"), gen_pins(pi, "recv"),
                                        gen_pins(po, 'send'), gen_pins(po, "recv"),
                                        gen_pins(wire, 'send'), gen_pins(wire, 'recv') )

    fout.write("module %s (%s, %s);\n\n" % (module, inputs, outputs))

    #output input, wire, output
    fout.write("input %s;\n\n" % inputs)
    fout.write("wire %s;\n\n" % wires)
    fout.write("output %s;\n\n" % outputs)
    
    fout.write("input scan_input;\n")
    fout.write("input scan_enable;\n")

    # output DFF and connect the scan chain
    fout.write("\n// scan chain begins here\n\n")

    last_input = "scan_input"
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
    
    # output all other statement
    for state in all_statements:
        # dff DFF_0(CK,G5,G10);
        elements = state.split(' ', 1)
        module = elements[0] #dff 
        (instance, pins) = elements[1].split('(') #DFF_0
        print instance, pins
        pins = map(lambda x:x.strip(), pins.rstrip(');').split(',')) # CK,G5,G10
        
        fout.write("%s SEND_%s(%s);\n" % (module, instance, gen_pins(pins, "send")))
        fout.write("%s RECV_%s(%s);\n" % (module, instance, gen_pins(pins, "recv")))        


    fout.write("endmodule\n")
    
    fout.write("//# %d DFFs" % (len(mid_dffs) + 2*len(dffs)))
    
if __name__ == '__main__':
    main()

#        # if the statements startswith "input", "output", "wire"
#        # we need to output them immediately
#        if elements[0] in ["input", "output", "wire"]:
#            
#            fout.write("%s %s\n" % (elements[0], gen_pins(elements[1], "send")))
#            fout.write("%s %s\n" % (elements[0], gen_pins(elements[1], "recv")))            
#        else:
