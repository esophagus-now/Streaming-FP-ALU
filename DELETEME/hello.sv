// This file is public domain, it can be freely copied without restrictions.
// SPDX-License-Identifier: CC0-1.0
`timescale 1ns/1ps
`default_nettype none

module hello(input logic clk);
    
    logic my_signal_1;
    logic my_signal_2;

    typedef struct packed {
        logic a;
        logic b;
    } my_struct_t;

    assign my_signal_1 = 1'bx;
    assign my_signal_2 = 0;
endmodule