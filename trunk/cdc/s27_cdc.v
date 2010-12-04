//# 4 inputs
//# 1 outputs
//# 3 D-type flipflops
//# 2 inverters
//# 8 gates (1 ANDs + 1 NANDs + 2 ORs + 4 NORs)

module dff (CK,Q,D);
    input CK,D;
    output Q;

    wire NM,NCK;
    trireg NQ,M;

    nmos N7 (M,D,NCK);
    not P3 (NM,M);
    nmos N9 (NQ,NM,CK);
    not P5 (Q,NQ);
    not P1 (NCK,CK);

endmodule

module s27(send_GND, send_VDD, send_CK, send_GG0, send_GG1, send_GG2, send_GG3, send_GG17, recv_GND, recv_VDD, recv_CK, recv_GG0, recv_GG1, recv_GG2, recv_GG3, recv_GG17);

input send_GND, send_VDD, send_CK, send_GG0, send_GG1, send_GG2, send_GG3, recv_GND, recv_VDD, recv_CK, recv_GG0, recv_GG1, recv_GG2, recv_GG3;
wire send_G5, send_G10, send_G6, send_G11, send_G7, send_G13, send_G14, send_G8, send_G15, send_G12, send_G16, send_G9, recv_G5, recv_G10, recv_G6, recv_G11, recv_G7, recv_G13, recv_G14, recv_G8, recv_G15, recv_G12, recv_G16, recv_G9;
output send_GG17, recv_GG17;
input scan_input;input scan_enable;// scan chain begins here

SDFFNSR SEND_DFF_0 (.CK(send_CK), .D(send_G10), .Q(send_G5), .SI(scan_input), .SE(scan_enable));
SDFFNSR SEND_DFF_1 (.CK(send_CK), .D(send_G11), .Q(send_G6), .SI(send_G5), .SE(scan_enable));
SDFFNSR SEND_DFF_2 (.CK(send_CK), .D(send_G13), .Q(send_G7), .SI(send_G6), .SE(scan_enable));
SDFFNSR SEND_I_DFF3 (.CK(send_CK), .D(send_HG0), .Q(send_G0), .SI(send_G7), .SE(scan_enable));
SDFFNSR SEND_I_DFF4 (.CK(send_CK), .D(send_HG1), .Q(send_G1), .SI(send_G0), .SE(scan_enable));
SDFFNSR SEND_I_DFF5 (.CK(send_CK), .D(send_HG2), .Q(send_G2), .SI(send_G1), .SE(scan_enable));
SDFFNSR SEND_I_DFF6 (.CK(send_CK), .D(send_HG3), .Q(send_G3), .SI(send_G2), .SE(scan_enable));
SDFFNSR SEND_O_DFF0 (.CK(send_CK), .D(send_G17), .Q(send_HG17), .SI(send_G3), .SE(scan_enable));
SDFFNSR RECV_DFF_0 (.CK(recv_CK), .D(recv_G10), .Q(recv_G5), .SI(send_HG17), .SE(scan_enable));
SDFFNSR RECV_DFF_1 (.CK(recv_CK), .D(recv_G11), .Q(recv_G6), .SI(recv_G5), .SE(scan_enable));
SDFFNSR RECV_DFF_2 (.CK(recv_CK), .D(recv_G13), .Q(recv_G7), .SI(recv_G6), .SE(scan_enable));
SDFFNSR RECV_I_DFF3 (.CK(recv_CK), .D(recv_HG0), .Q(recv_G0), .SI(recv_G7), .SE(scan_enable));
SDFFNSR RECV_I_DFF4 (.CK(recv_CK), .D(recv_HG1), .Q(recv_G1), .SI(recv_G0), .SE(scan_enable));
SDFFNSR RECV_I_DFF5 (.CK(recv_CK), .D(recv_HG2), .Q(recv_G2), .SI(recv_G1), .SE(scan_enable));
SDFFNSR RECV_I_DFF6 (.CK(recv_CK), .D(recv_HG3), .Q(recv_G3), .SI(recv_G2), .SE(scan_enable));
SDFFNSR RECV_O_DFF0 (.CK(recv_CK), .D(recv_G17), .Q(recv_HG17), .SI(recv_G3), .SE(scan_enable));
// scan chain ends here

not SEND_NOT_0(send_G14, send_G0);
not RECV_NOT_0(recv_G14, recv_G0);
not SEND_NOT_1(send_G17, send_G11);
not RECV_NOT_1(recv_G17, recv_G11);
and SEND_AND2_0(send_G8, send_G14, send_G6);
and RECV_AND2_0(recv_G8, recv_G14, recv_G6);
or SEND_OR2_0(send_G15, send_G12, send_G8);
or RECV_OR2_0(recv_G15, recv_G12, recv_G8);
or SEND_OR2_1(send_G16, send_G3, send_G8);
or RECV_OR2_1(recv_G16, recv_G3, recv_G8);
nand SEND_NAND2_0(send_G9, send_G16, send_G15);
nand RECV_NAND2_0(recv_G9, recv_G16, recv_G15);
nor SEND_NOR2_0(send_G10, send_G14, send_G11);
nor RECV_NOR2_0(recv_G10, recv_G14, recv_G11);
nor SEND_NOR2_1(send_G11, send_G5, send_G9);
nor RECV_NOR2_1(recv_G11, recv_G5, recv_G9);
nor SEND_NOR2_2(send_G12, send_G1, send_G7);
nor RECV_NOR2_2(recv_G12, recv_G1, recv_G7);
nor SEND_NOR2_3(send_G13, send_G2, send_G12);
nor RECV_NOR2_3(recv_G13, recv_G2, recv_G12);
endmodule
