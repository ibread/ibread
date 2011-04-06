#!/usr/bin/env python

import re

SEND_CLK = 'bit_clk_pad_i'
RECV_CLK = 'clk_i'

fin = open("cdc_path.txt")

fout = open("recv_dff.txt", "w+")

lines = fin.readlines()

for l in lines:
    # g29896:Y(n_11202) --  u1_slt2_reg_b19b[bit_clk_pad_i] ===> g40434 [MX2X1 @ clk_i]:B(in_slt_845) ===> u15_crac_din_reg_b15b[clk_i](n_1083) -- g37365:B1
    r = re.findall(r'([^ ]+)\[%s\]' % SEND_CLK, l)
    if len(r) != 0:
        fout.write(r[0] + " ")
    else:
        fout.write('NO_SENDER ')

    r = re.findall(r'([^ ]+)\[%s\]' % RECV_CLK, l)
    if len(r) != 0:
        fout.write(r[0] + "\n")
    else:
        fout.write('NO_RECV')

fin.close()
fout.close()
