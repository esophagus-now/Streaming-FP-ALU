// This file is public domain, it can be freely copied without restrictions.
// SPDX-License-Identifier: CC0-1.0
`timescale 1ns/100ps

module hello (
    input i_clk,
    input i_reset_n,

    input i_A,
    input i_B,
    input i_vld,
    input i_last,
    output o_rdy,

    output o_S,
    output o_overflow, //Only valid on last flit
    output o_vld,
    output o_last,
    input i_rdy
);
    /////////////////////
    // State variables //
    /////////////////////
    
    wire carry;
    wire carry_next;
    mm_flop carry_flop (i_clk, i_reset_n, carry_next, carry);
    
    wire sum = i_A ^ i_B ^ carry;
    assign carry_next = !i_last && (
        (i_A & i_B) |
        (i_A & carry) |
        (i_B & carry)
    );


    ////////////////////
    // Assign outputs //
    ////////////////////
    assign o_rdy = i_rdy;
    assign o_vld = i_vld;
    assign o_last = i_last;
    assign o_S = sum;
    assign o_overflow = carry_next;
    
endmodule