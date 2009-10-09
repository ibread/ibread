#!/usr/bin/python
#encoding: utf-8

#@file: cts.py
#@brief: convert traditional chinese filenames into simplified ones
#@usage: ./cts.py [-r] [-s | -t] PATH_NAME | FILENAME
#       -r: recursively
#       -t: simplified => traditional
#       -s: traditional => simplified, by default
#
#       all files under PATH_NAME will be converted, but not recusively

from langconv import *
from optparse import OptionParser
from glob import *
import sys, os

def convert(path, recur=False, simple=True, verbose=1):
    '''
    @brief: convert path name from SimplifiedChinese=>TraditionalChinese or the opposite
        If it's a single file, just rename it
        If it's a directory and recursive is OFF, just rename it
            Otherwise, recursively rename files under it
    @args:
        file: the file/dir need to be renamed
        simple: SC=>TC or TC=>SC
        verbose: wether print filename been processing or not
    '''
    if os.path.isfile(path):
        s_convert(path, simple, verbose)
    elif os.path.exists(path):
        path = s_convert(path, simple, verbose)
        if recur:
            for f in glob(path+"/*"):
                convert(f.encode('utf8'), True, simple, verbose)
    else:
        print "You gave the path which doesn't exist :(", path

def s_convert(file, simple=True, verbose=1):
    '''
    @descrition: convert name of a single file/directory
    @args:
        file: the file/dir need to be renamed
        simple: SC=>TC or TC=>SC
        verbose: wether print filename been processing or not
    @return:
        new name
    '''
    if simple:
        c = Converter('zh-hans')
    else:
        c = Converter('zh-hant')
    
    new = c.convert(file.decode('utf8'))
    if new != file.decode('utf8'):
        if verbose:
            print file, '===>', new            
        os.rename(file, new)
    
    return new   

def main():
    parser = OptionParser(version="%prog 0.1", 
        usage="Usages: %prog [option] FILE | DIRECTORY ...")
    
    parser.add_option("-r", "--recursive", dest="recur",
        action="store_true", default=False,
        help="recursively process current directory")
    parser.add_option("-s", "--simplified", dest="simple", 
        action="store_true", default=True,
        help="Traditional => Simpleified Chinese, By default")
    parser.add_option("-t", "--traditional", dest="simple", 
        action="store_false", default=True,
        help="Simpleified => Traditional Chinese")
    parser.add_option("-q", "--quiet", dest="verbose", 
        action="store_false", default=True,
        help="Verbose mode, display every file been renamed")
  
    (options, args) = parser.parse_args()
    
    if len(args) == 0:
        parser.print_help()
        sys.exit(1)
    
    for path in args:
        convert(path, options.recur, options.simple, options.verbose)

if __name__ == '__main__':
    main()
    print 'Done.'
