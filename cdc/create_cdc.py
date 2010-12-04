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
    wires = []
    # dffs
    dffs = []
    # all statements
    all_statements = []
    
    for line in fin:
        if line.count("module s27") > 0:
            indicator = True

        if indicator and line.count("endmodule") > 0:
            indicator = False
    
        # Do nothing if we're outside of module or encountering comments
        if (not indicator) or line.strip().startswith("//"):
            fout.write(line)
            continue
    
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
        elif elements[0] == "wires":
            wires.extend(elements[1].strip(';').split(','))
        elif elements[0] == "dff":
            dffs.extend(elements[1]) # DFF_0(CK,G5,G10);
        else:
            all_statements.append(statement)

        # if the statements startswith "input", "output", "wire"
        # we need to output them immediately
        if elements[0] in ["input", "output", "wire"]:
            
            fout.write("%s %s\n" % (elements[0], gen_pins(elements[1], "send")))
            fout.write("%s %s\n" % (elements[0], gen_pins(elements[1], "recv")))            
        else:
            # dff DFF_0(CK,G5,G10);
            module = elements[0] #dff 
            (instance, pins) = elements[1].split('(') #DFF_0
            pins = pins.rstrip(');') # CK,G5,G10
            
            if elements[0] == "module": # module s27
                fout.write("%s %s(%s,%s);\n" % (module, instance, gen_pins(pins, "send"), gen_pins(pins, "recv")))
            else:
                fout.write("%s SEND_%s(%s);\n" % (module, instance, gen_pins(pins, "send")))
                fout.write("%s RECV_%s(%s);\n" % (module, instance, gen_pins(pins, "recv")))
            
        # initialize statement for next round 
        statement = ""

    # add dffs at the start & the end of the circuits
    # input: i1 => dff(CK, i1, ii1)
    # output: o1 => dff(CK, oo1, o1)		
    for i in xrange(len(pi)):
        # these are not primary inputs
        if i in ["CK", "GNN", "VDD"]:
            continue
        dffs.extend("I_DFF(CK, %s, %s)" % (pi[i], "G"+pi[i]))
        pi[i] = "G" + pi[i]
        
    for i in xrange(len(po)):
        dffs.extend("O_DFF(CK, %s, %s)" % ("G"+pi[i], pi[i]))
        po[i] = "G" + po[i]
            
    # output module
    # module s27 (CK, GND, ...)
    fout.write("module %s(%s, %s);\n" % (instance, gen_pins(pi, "send"), gen_pins(pins, "recv")))
    
    #output input
        
        


if __name__ == '__main__':
    main()
