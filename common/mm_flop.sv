//It's just a flop. Designed to be less annoying than
//typing that friggin always block every time

module mm_flop # ( 
    parameter WIDTH = 1,
    parameter [WIDTH -1:0] PON_VAL = '0
) (
    input i_clk,
    input i_reset_n,

    input i_D,
    output o_Q
);
    reg [WIDTH -1:0] Q;
    
    always_ff @(posedge i_clk) begin
        if (!i_reset_n) begin
            Q <= PON_VAL;
        end else begin
            Q <= i_D;
        end
    end

    assign o_Q = Q;
endmodule