#!/usr/bin/python
# @file: update.py
# @author: Zhiqiu Kong <breaddawson@gmail.com>
# @date: Jan 24, 2010
# @brief: This script is used to check retrieve the latest chinese ip database
#       Here're several features:        
#       1. Check if update is available (via md5_sum) 
#       2. 2 output formats for net address: 
#           -c: CIDR format, 1.2.0.0/16
#           -d: Dot Deciaml format, 1.2.0.0 255.255.0.0
#       3. cutomized output formats, such as the following format used for openvpn:
#               push "route 1.2.0.0 255.255.0.0 net_gateway 5"

import os,sys
from optparse import OptionParser

def is_updated(out_file):
    # retrieve cn ips from apnic and preprocess
    status = os.system("curl -s http://ftp.apnic.net/apnic/dbase/data/country-ipv4.lst | grep cn | grep -oE [0-9.]+/[0-9]+ > pre_cn_db.lst");
    if status != 0:
        print "Error when downloading ip database or it's in invalid formate!"
        sys.exit(1)

    # check if update is available or not
    status = os.system("md5 pre_cn_db.lst %s &> new_md5_sig && diff new_md5_sig md5_sig &> /dev/null" % (out_file) )
    print "status=%d" % (status)
    return status

def CIDR_2_dot_decimal(origin):
    '''
    @desciption: given original net address in CIDR format 
                 such as "1.2.3.4/8",
                 return "1.2.3.4 255.0.0.0"
    @param:
        origin: original net address in CIDR format
    @return:
        net address and netmask as a string
    '''
    slash_pos = origin.find('/')
    if slash_pos == -1:
        print "Error!! Only net address in CIDR is accepted!!"
        print "example: 1.2.0.0/16"
        sys.exit(1)

    len = int(origin[slash_pos+1:].strip())
    netmask = ""
    for i in range(4):
        k = (len>8) and 8 or len
        netmask = netmask+str(((2**k)-1)<<(8-k))+"."
        if len > 8:
            len -= 8
        else:
            len = 0
    return "%s %s" % (origin[:slash_pos], netmask[:-1])

def update_ip_seg(out_file, CIDR=0, format="%s"):
    fin = open("pre_cn_db.lst","r")
    fout = open(out_file, "w+")

    for line in fin.readlines():
        # convert "1.2/16" to "1.2.0.0/16"
        zeroes = 3-line.count('.')
        result = line[:line.find('/')]
        for i in range(zeroes):
            result += ".0" 
        result += line[line.find('/'):].strip()

        # which format?
        # 1.2.0.0/8 (CIDR) or 1.2.0.0 255.0.0.0 (dot decimal)?
        if CIDR:
            fout.write(format % (result))
        else:
            fout.write(format % (CIDR_2_dot_decimal(result)))


if __name__ == "__main__":
    # add option parser
    parser = OptionParser()
    parser.add_option("-c", dest="CIDR", action="store_true", default=True,
                        help="use CIDR format: 1.2.0.0/16")
    parser.add_option("-d", dest="CIDR", action="store_true",
                        help="use Dot Decimal: 1.2.0.0 255.255.0.0")
    parser.add_option("-f", dest="force_up", action="store_true", default=False,
                        help="force to update cn net addess")
    parser.add_option("-o", dest="outfile", type="string",
                        help="Place cn net address in file OUTFILE")
    parser.add_option("--format", type="string", dest="outformat",
                        help="customized output format")
    parser.add_option("-p", "--paveo", dest="paveo", action="store_true", 
                        default=False, 
                        help="argument provided for paveo's openvpn")
    (options, args) = parser.parse_args()

    if options.outformat:
        out_format = options.outformat
    else:
        out_format = "%s\n"

    if options.outfile:
        out_file = options.outfile
    else:
        out_file = "cn_net_addr.lst"

    CIDR = options.CIDR
    force = options.force_up

    if options.paveo:
        CIDR = False
        out_format = "push \"route %s net_gateway 5\"\n\n"
    
    print "* Checking ip database..."

    if is_updated(out_file) or force:
        print "* Update available: ip database from apnic"
        print "* Preprocessing..."
        update_ip_seg(out_file, CIDR, out_format)
        print "* Updating md5 signature..."
        os.system("md5 pre_cn_db.lst cn_net_addr.lst > md5_sig")
        print "* Done. New cn_net_addr.lst is ready for route tables"
    else:
        print "* Nothing new, cn_net_addr.lst remains untouched." 
    
    # clear temp files
    os.system("rm pre_cn_db.lst new_md5_sig")
