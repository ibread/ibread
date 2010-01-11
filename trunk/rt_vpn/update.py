#!/usr/bin/python

import os,sys

def is_updated():

    # retrieve cn ips from apnic and preprocess
    status = os.system("curl -s http://ftp.apnic.net/apnic/dbase/data/country-ipv4.lst | grep cn | grep -oE [0-9.]+/[0-9]+ > cn_ipv4.lst");
    if status != 0:
        print "Error when downloading ip database or it's in invalid formate!"
        sys.exit(1)

    # check if it is new
    status = os.system("md5 cn_ipv4.lst > new_md5_sig && diff new_md5_sig md5_sig &> /dev/null")
    if status == 0:
        return 0
    else:
        return 1

def update_ip_seg():
    ip_seg= open("cn_ipv4.lst","r")
    mac_ip_seg = open("mac_cn_ip.lst", "w+")

    for line in ip_seg.readlines():
        zeroes = 3-line.count('.')
        result = line[:line.find('/')]
        for i in range(zeroes):
            result += ".0" 
        result += line[line.find('/'):]
        mac_ip_seg.write(result)

if __name__ == "__main__":
    print "* Checking ip database..."

    if is_updated():
        print "* Update available: ip database from apnic"
        print "* Preprocessing..."
        update_ip_seg()

        print "* Updating md5 signature..."
        os.system("md5 cn_ipv4.lst > md5_sig")

        print "* Done. New mac_cn_ipv4.lst is ready for route tables"
    else:
        print "* Nothing new, mac_cn_ipv4.lst remains untouched." 
    
    os.system("rm cn_ipv4.lst new_md5_sig")
