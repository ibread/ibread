#!/usr/bin/env python

import re
fin = open("cdc_path.txt")

fout = open("recv_dff.txt", "w+")

lines = fin.readlines()

for l in lines:
    r = re.findall(r'([^ ]+)\[clk_i\]', l)
    if len(r) != 0:
        fout.write(r[0] + "\n")

fin.close()
fout.close()
