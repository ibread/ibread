#!/usr/bin/env python
#               receiver    sender
# round 1:        0           N/A
# round 2:        0           1
# round 3:        1           1
import os, sys, re

# we need two kinds of files: the bench file and the out file
# actually, we need the directory of these two kinds of files
# because they are corresponding to each other one by one

if len(sys.argv) < 3:
    print "Usage: %s BENCH_DIR/../ ROUND" % sys.argv[0]
    sys.exit(1)

BASE_DIR = sys.argv[1]
BENCH_DIR = BASE_DIR+"/bench"
ROUND = sys.argv[2]
OUT_DIR = BASE_DIR+"/ms_out"+str(int(ROUND)-1)

benches = os.listdir(BENCH_DIR)

# the value of every round: receiver and sender
values = [(0,0), (0,1), (1,1)]


NEW_BENCH_DIR = os.path.abspath(BASE_DIR) + "/bench_r"+ROUND
os.system("mkdir -p %s" % NEW_BENCH_DIR)

for i in xrange(len(benches)):
    # copy to creat a new bench file
    new_file = NEW_BENCH_DIR+'/'+benches[i]
    os.system("cp %s %s" % (BENCH_DIR+"/"+benches[i], new_file))
    # search and replace the corresponding line in bench file
    # change the output directory
    os.system(r"sed -i 's/msout/msout%s/g' %s" % (ROUND, new_file))
    if ROUND=="1":
        # on the first run, just change TopTester.CUT.blabla
        # add receiver_out = 0, sender_out = 0
        os.system(r"sed -i 's/b1) \/\/ /b0 /g' %s" % new_file)
    else: # the 2nd or 3rd run
        ms_outs = os.listdir(OUT_DIR)
        # get value from the out files of modelsim
        out_lines = open(OUT_DIR+ms_outs[i], "r").readlines()
        dff_outs = out_lines[1].split('=')[1].strip()
        pis = out_lines[3].split('=')[1].strip()
        inits = out_lines[4].split('=')[1].strip()

        # dff_outs = "12345"
        # pis = "67890"
        # inits = "11111"
        # change the line: test_vector = 10'b010101010101; // only the inputs
        os.system('sed -i "s/= .*; \/\/ only the inputs/= %s; \/\/ only the inputs/g" %s' % ( str(len(pis+dff_outs))+ "'b"+pis+dff_outs, new_file))
        # change the line: ff results=5'b010101;
        # os.system('sed -i "s/ff results=.*)/ff resutls=%%b\n, %s)/g" %s' % ( str(len(dff_outs)) +dff_outs, new_file))
        os.system('sed -i "s/ff results=.*)/ff resutls=%%b\\\\\\\\n\\", %s)/g" %s' % ( str(len(dff_outs)) + "'b" + dff_outs, new_file))

        # change the if line
        # round 2: 1 0
        # round 3: 1 x
        if ROUND=='2':
            os.system(r"sed -i 's/b1) \/\/ /b0 /g' %s" % new_file)
            os.system(r"sed -i 's/b0)$/b1)/g' %s" % new_file)
        elif ROUND=='3':
            os.system(r"sed -i 's/b0) \//b1) \//g' %s" % new_file)
    
    
