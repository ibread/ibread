#!/usr/bin/env python

import os, sys, fnmatch
import inspect

def convert_time (time = "01:10:37.915249"):
    t = time.split('.')
    i = t[0]
    f = t[1]
    
    i = i.split(":")
    i = int(i[0])*3600 + int(i[1])*60 + int(i[2])
    f = float("0." + f)
    if f < 0.00000001:
        f = 0.00000001
    
    ret = float(i) + f
    # print ret
    return ret


class Operations:
    def __init__(self):
        self.ops = 0
        self.size = 0
        
        self.seq_ops = 0
        self.seq_size = 0
        self.random_ops = 0
        self.random_size = 0

        self.last_offset = -1
        self.last_size = 0

    def add(self, size, offset=-1, random=True):
        self.ops += 1
        self.size += size
        
        self.last_offset = offset
        self.last_size = size
        
        if random:
            self.random_ops += 1
            self.random_size += size
        else:
            self.seq_ops += 1
            self.seq_size += size

def analyze(result_file):
    '''
    Given the results provided by filter, analyze and then provide the following info:

    1. Read/Write data
    2. Read/Write #operations
    3. Read/Write data ratio and operations ratio

    We need also to find out the pattern of read/write operations, say sequential or random.
    '''

    # every line of the result is formatted as following:
    # 
    # time	client	server	operation_type	file_handler	uid	pid	size	offset
    # 21:24:08.341428	192.168.1.164.4181390566	192.168.1.163.nfs	access	70001:4061:0:5eb1508e:994e1024:7a43a6b2:eaca5990				
    #
    # 1. Not all results have 'offset' domain
    # 2. For client, the format is IP_Address.Package_Index
    # 3. there are three types of operations: access, write and read, where access is classified as write operation
    #

    # this is the number of domains in every log entry
    # if this line is changed, plz do search FORMAT and change line below it accordingly
    FORMAT = "time_start	client	server	operation_type	file_handler	uid	pid	size	offset	record_count	time_end"

    DOMAIN_NUM = len(FORMAT.split())

    # for debugging
    c = inspect.currentframe()
    
    try:
        fin = open(result_file)
    except IOError:
        print "Error, plz check the file %s" % result_file
        return

    Reads = Operations()
    Writes = Operations()

    total_duration = 0
    total_lines = 0
    
    first_start = 0.0
    last_end = 0.0

    for line in fin:
        total_lines += 1
        if line.strip().startswith('time'):
            continue

        line_bak = line
        line = line.split()
        if len(line) < DOMAIN_NUM:
            line.extend([0] * (DOMAIN_NUM-len(line)))
        elif len(line) > DOMAIN_NUM:
            line = line[:DOMAIN_NUM]

        # change this according to FORMAT
        # time_start	client	server	operation_type	file_handler	uid	pid	size	offset	record_count	time_end

        time_start, client, server, op_type, handler, uid, pid, size, offset, record_count, time_end = line

        if size == "na":
            print "Fatal Error!! Size is equal to N/A, the original log is as following"
            print "   ", line_bak
            return

        if offset == "na":
            offset = -1
        
        try:
            size = int(size)
            offset = int(offset)
        except ValueError:
            print "Error!! size %s or offset %s is not a number! " % (size, offset)
            return
            
        try:
            op_type = op_type.strip()
        except AttributeError:
            print "[Debug] Error: AttrbitueError on line %s" % int(c.f_lineno)
            print " result_file = result_file"
            print " op_type = %s, line = %s" % (op_type, line)
            continue
        
        if op_type.strip() == "read": # read operation
            # the operation is random if it is the first one
            # or it does not follow the predecessor package
            random = Reads.last_offset == -1 or (Reads.last_offset+Reads.last_size != offset)
            Reads.add(size, offset, random)
        else:
            random = Writes.last_offset == -1 or (Writes.last_offset+Writes.last_size != offset)
            Writes.add(size)

        duration = 0

        if "na" not in [time_start, time_end]:
            try:
                duration = convert_time(time_end) - convert_time(time_start)
                last_end = convert_time(time_end)
                if total_line == 1:
                    first_start = convert_time(time_start)
            except AttributeError:
                print "[Debug] AttriError on line %s" % c.f_lineno
                print " time_end, time_start = %s, %s" % (time_end, time_start)
            if duration < 0:
                print "Error!! Duration < 0"

        if duration > 0:
            # print "d", duration
            total_duration += duration

    if total_lines > 0:
        # print "\nClients: %s" % client
        print "Handler: %s" % handler
        file_size = os.path.getsize(result_file)
        print "Log Size: %s B" % file_size
        print "Duration: %s s" % duration

        print "Reads:  #%5s:%9sB    Ran: #%5s:%9sB    Seq: #%5s:%9sB" % \
              (Reads.ops, Reads.size, Reads.random_ops, Reads.random_size, Reads.seq_ops, Reads.seq_size)

        print "Writes: #%5s:%9sB    Ran: #%5s:%9sB    Seq: #%5s:%9sB" % \
              (Writes.ops, Writes.size, Writes.random_ops, Writes.random_size, Writes.seq_ops, Writes.seq_size)

        ret = [handler, file_size, duration, Reads.ops, Reads.size, Reads.random_ops, Reads.random_size, Reads.seq_ops, Reads.seq_size, \
               Writes.random_ops, Writes.random_size, Writes.seq_ops, Writes.seq_size]
        return ret
    else:
        return None
        
def process_all():
    RESULTS_DIR = "./results"

    results = fnmatch.filter(os.listdir(RESULTS_DIR), '*.txt')


    # > 1K
    # < 1K
    # read: random ops, random size, seq ops, seq size,
    # write: random ops, random size, seq ops, seq size
    c0 = [0] * 9
    c1 = [0] * 9
    c2 = [0] * 9
    
    index = 1
    # print results
    for r in results:
        print "\n#"+str(index), r
        index += 1
        ret = analyze(RESULTS_DIR+ "/" + r)
        if ret == None:
            print "[Debug] results for #%d file %s is 0" % (index, r)
            continue

        if ret[1] > 10*1024:
            c0[8] += 1
            for i in xrange(len(c0)-1):
                c0[i] += ret[5+i]
                
        elif ret[1] > 1024:
            c1[8] += 1
            for i in xrange(len(c1)-1):
                c1[i] += ret[5+i]
        else:
            c2[8] += 1
            for i in xrange(len(c1)-1):
                c2[i] += ret[5+i]
                
    print c0
    print c1
    print c2


if __name__ == "__main__":
    process_all()
