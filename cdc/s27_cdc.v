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

module s27(send_GND, send_VDD, send_CK, send_G0, send_G1, send_G17, send_G2, send_G3,recv_GND, recv_VDD, recv_CK, recv_G0, recv_G1, recv_G17, recv_G2, recv_G3);
input send_GND, send_VDD, send_CK, send_G0, send_G1, send_G2, send_G3;
input recv_GND, recv_VDD, recv_CK, recv_G0, recv_G1, recv_G2, recv_G3;
output send_G17;
output recv_G17;
wire send_G5, send_G10, send_G6, send_G11, send_G7, send_G13, send_G14, send_G8, send_G15, send_G12, send_G16, send_G9;
wire recv_G5, recv_G10, recv_G6, recv_G11, recv_G7, recv_G13, recv_G14, recv_G8, recv_G15, recv_G12, recv_G16, recv_G9;
dff SEND_DFF_0(send_CK, send_G5, send_G10);
dff RECV_DFF_0(recv_CK, recv_G5, recv_G10);
dff SEND_DFF_1(send_CK, send_G6, send_G11);
dff RECV_DFF_1(recv_CK, recv_G6, recv_G11);
dff SEND_DFF_2(send_CK, send_G7, send_G13);
dff RECV_DFF_2(recv_CK, recv_G7, recv_G13);
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
