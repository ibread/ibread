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

module s27 (send_CK, send_GND, send_VDD, recv_CK, recv_GND, recv_VDD, hsend_G0, hsend_G1, hsend_G2, hsend_G3, hrecv_G1, hrecv_G2, hrecv_G3, hrecv_G17);

input send_CK, send_GND, send_VDD, recv_CK, recv_GND, recv_VDD, hsend_G0, hsend_G1, hsend_G2, hsend_G3, hrecv_G1, hrecv_G2, hrecv_G3;

wire send_G0, send_G1, send_G2, send_G3, recv_G0, recv_G1, recv_G2, recv_G3, send_G17, recv_G17, send_G5, send_G10, send_G6, send_G11, send_G7, send_G13, send_G14, send_G8, send_G15, send_G12, send_G16, send_G9, recv_G5, recv_G10, recv_G6, recv_G11, recv_G7, recv_G13, recv_G14, recv_G8, recv_G15, recv_G12, recv_G16, recv_G9;

output hrecv_G17;

input scan_input;
input scan_enable;

// scan chain begins here

SDFFNSR SEND_I_DFF0(.CK(send_CK), .D(hsend_G0), .Q(send_G0), .SI(scan_input), .SE(scan_enable));
SDFFNSR RECV_I_DFF0(.CK(recv_CK), .D(hrecv_G0), .Q(recv_G0), .SI(send_G0), .SE(scan_enable));
SDFFNSR SEND_I_DFF1(.CK(send_CK), .D(hsend_G1), .Q(send_G1), .SI(recv_G0), .SE(scan_enable));
SDFFNSR RECV_I_DFF1(.CK(recv_CK), .D(hrecv_G1), .Q(recv_G1), .SI(send_G1), .SE(scan_enable));
SDFFNSR SEND_I_DFF2(.CK(send_CK), .D(hsend_G2), .Q(send_G2), .SI(recv_G1), .SE(scan_enable));
SDFFNSR RECV_I_DFF2(.CK(recv_CK), .D(hrecv_G2), .Q(recv_G2), .SI(send_G2), .SE(scan_enable));
SDFFNSR SEND_I_DFF3(.CK(send_CK), .D(hsend_G3), .Q(send_G3), .SI(recv_G2), .SE(scan_enable));
SDFFNSR RECV_I_DFF3(.CK(recv_CK), .D(hrecv_G3), .Q(recv_G3), .SI(send_G3), .SE(scan_enable));
SDFFNSR RECV_O_DFF0(.CK(recv_CK), .D(recv_G17), .Q(hrecv_G17), .SI(recv_G3), .SE(scan_enable));
SDFFNSR MID_DFF0(.CK(send_CK), .D(hsend_G17), .Q(hrecv_G0), .SI(hrecv_G17), .SE(scan_enable));
// All orignal DFFs are extended into 2 copies
SDFFNSR SEND_DFF_0 (.CK(send_CK), .D(send_G10), .Q(send_G5), .SI(hrecv_G0), .SE(scan_enable));
SDFFNSR SEND_DFF_1 (.CK(send_CK), .D(send_G11), .Q(send_G6), .SI(send_G5), .SE(scan_enable));
SDFFNSR SEND_DFF_2 (.CK(send_CK), .D(send_G13), .Q(send_G7), .SI(send_G6), .SE(scan_enable));
SDFFNSR RECV_DFF_0 (.CK(recv_CK), .D(recv_G10), .Q(recv_G5), .SI(send_G7), .SE(scan_enable));
SDFFNSR RECV_DFF_1 (.CK(recv_CK), .D(recv_G11), .Q(recv_G6), .SI(recv_G5), .SE(scan_enable));
SDFFNSR RECV_DFF_2 (.CK(recv_CK), .D(recv_G13), .Q(recv_G7), .SI(recv_G6), .SE(scan_enable));
//END: All orignal DFFs are extended into 2 copies// scan chain ends here

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
