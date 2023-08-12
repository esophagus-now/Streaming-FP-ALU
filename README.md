### Streaming floating-point ALU

Idea: typically an FP ALU will do something like having a `n` by `n` multiplier/adder/etc. with a bunch of renormalization logic. For timing this will usually be split into several clock cycles. Usually we want the number of clock cycles to be small to reduce latency.

Well, that's nice, but sometimes it's helpful to have different design variations. In this case, I want to completely give up on latency and instead minimize area (and power as a secondary concern). The idea is to have a "1 by 1" multiplier/adder (with carrying logic and O(1) memory) and shift our inputs in one bit at a time. The expected benefits are:
- Less area
- Choose FP precision at runtime
- By having an array of these 1-bit ALUs, we have the opportunity to apply permutations on each cycle
  - For example, a Benes network
- Potential power savings by gating the clock when the rest of the inputs are zero

The downside is higher latency. This means that dependent calculations will be very slow. Maybe we can do some clever forwarding to deal with this, but we'll think about that later.

### Unanswered design questions

- Do we want to be compliant to the IEEE standard?
- What kind of rounding modes do we want to make available?

### Design flow

Every module will have some kind of "designer-level" testbench. Sometimes this will be simpler to just do up in verilog, and sometimes it will be helpful to use cocotb.

For the initial stage of the project, we just want to make one streaming FP ALU and see if it works. Later, we may try to instantiate two or more to try out different ofrwarding techniques to reduce latency on dependent ops. After that we could try to instantiate a large array and prove that we can do large and useful calculations. For these larger testbenches, it may be worthwhile to use UVM. 


### Steps

First do an integer streaming adder, just to bring up a good design flow