
module buf1 (out, in);
    output out;
    input in;
    buf (out, in);
endmodule
    module n_77_domain (scan_enable, scan_data_in, scan_data_out, n_77, sdata_pad_i, );

input scan_enable, scan_data_in, n_77, sdata_pad_i;
output scan_data_out, ;
// scan chain begins here
SDFFNSRN u1_sdata_in_r_reg (.CK(n_77), .D(sdata_pad_i), .Q(u1_sdata_in_r), .SO(u1_sdata_in_r), .SE(scan_enable), .SI(scan_data_in));
// scan chain ends here

 buf1 BUFbread(scan_data_out, u1_sdata_in_r);

endmodule