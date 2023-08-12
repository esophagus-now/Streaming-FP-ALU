# test_my_design.py (simple)

import cocotb
import cocotb.clock
import random
from cocotb.triggers import Timer
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.triggers import ReadOnly
from cocotb.triggers import ReadWrite
from cocotb.triggers import NextTimeStep

async def reset_thread(rst, delay=10, active_low=True):
    rst.value = 0 if active_low else 1
    await Timer(delay, units="ns")
    rst.value = 1 if active_low else 0

# If payload is a list, send each element one-by-one.
# payload can also be a single element which results in
# sending a single flit.
#
# All of the wire bindings (except clk) are optional.
# If data is provided, it will be driven according to
# the payload. If not, you will still need to place
# dummy items into payload so that the function knows
# how many flits to send. You can make data a list of
# signals, in which case you must make each payload
# element a list/tuple of the same length, and they
# will be assigned in the obvious way.
#
# If valid is provided, it will be driven whenever the
# DUT can read our output. If you set vld_only_when_rdy,
# then valid will be driven to 0 whenever rdy is 0.
#
# If ready is provided, this function will honour the 
# usual handshaking scheme. If not, it will assume the
# DUT is always ready.
#
# If last is provided, it will go to 1 when sending 
# the last element of payload and be 0 otherwise.
#
# Setting timeout to 0 means "no timeout". Otherwise,
# if the number of cycles between two flits exceeds 
# timeout, throw an error.
#
# TODO? Add options to change polarities? 
async def hs_send(
    payload, 
    clk,
    data=None, last=None, 
    vld=None, rdy=None,
    vld_only_when_rdy=False,
    timeout=128
):
    if type(payload) != list and type(payload) != tuple:
        payload = [payload]

    if (
        data is not None and
        (type(data) != list and type(data) != tuple)
    ):
        data = [data]
        
    l = len(payload)
    
    for i in range(l):
        flit = payload[i]
        if type(flit) != list and type(flit) != tuple:
            flit = [flit]
        
        if data is not None:
            for j in range(len(data)):
                data[j].value = flit[j]

        if last is not None:
            last.value = 1 if (i == (l-1)) else 0
        
        cycles = 0
        while True:
            if vld is not None:
                if vld_only_when_rdy:
                    # Ugly... need a way to wait for any
                    # PLI assignments to settle before we
                    # read from ready. This is definitely
                    # not ideal. FIXME
                    await FallingEdge(clk)
                    is_rdy = ( 
                        (rdy is None) or 
                        (rdy.value.integer == 1)
                    )
                    vld.value = 1 if is_rdy else 0
                else:
                    # TODO: random suppression
                    vld.value = 1

            await RisingEdge(clk) # In case rdy depends on vld
            is_rdy = ( 
                (rdy is None) or 
                (rdy.value.integer == 1)
            )
            if is_rdy:
                break
            cycles += 1
            if timeout != 0 and cycles > timeout:
                assert False, "Timed out sending a flit"

    # Clear vld back to 0. This might cause a glitch in
    # the waveform but it's OK
    if vld is not None:
        vld.value = 0

# All of the wire bindings (except clk) are optional.
#
# If data is provided, then the value(s) from each flit
# will be returned in a list. If not, then this function
# will return a list of 'None' objects to indicate how
# many flits were received. You can provide a list/tuple
# of signals, and each element of the returned data will
# be a list/tuple of the same size with one entry for each
# signal
# 
# If valid is provided, it will be sampled to determine
# when data can be read. If not, the function will assume
# the DUT data is always valid.
# 
# If ready is provided, this function will drive it to 
# 1 for as long as it is listening for data. TODO: allow
# random suppression modes
# 
# If last is provided, it will be used to determine when
# to stop reading datums and return. If not provided, then
# this function only reads a single flit. TIP: if you want
# to read the last bit, but only read flits one at a time,
# then simply add the last signal into the data tuple
#
# Setting timeout to 0 means "no timeout". Otherwise,
# if the number of cycles between two flits exceeds 
# timeout, throw an error.
#
# TODO? Add options to change polarities? 
async def hs_recv(
    clk,
    data=None, last=None, 
    vld=None, rdy=None,
    timeout=128
):
    # TODO: random suppression support
    if rdy is not None:
        rdy.value = 1

    cycles = 0

    ret = []

    while True:
        await ReadOnly()
        is_vld = (vld is None or vld.value.integer == 1)
        if is_vld:
            cycles = 0
            if data is None:
                ret.append(None)
            elif type(data) == tuple:
                vals = []
                for sig in data:
                    vals.append(sig.value)
                ret.append(tuple(vals))
            elif type(data) == list:
                vals = []
                for sig in data:
                    vals.append(sig.value)
                ret.append(vals)
            else:
                ret.append(data.value)
        await RisingEdge(clk)
        is_last = (last is None or last.value.integer == 1)
        if is_last:
            break
        cycles += 1
        assert cycles < timeout, "Timed out waiting to receive a flit"
    
    rdy.value = 0

    return ret


# num_cycles is how long to use this driver. If 0,
# then driver runs forever
async def random_driver(sig, clk, num_cycles=0):
    assert sig.value.n_bits, "I guess this doesn't have n_bits"
    
    cycles = 0
    while num_cycles == 0 or cycles < num_cycles:
        sig.value = random.randint(0,(1<<sig.value.n_bits)-1)
        await RisingEdge(clk)
        cycles += 1

async def timeout_thread(delay, units="ns"):
    await Timer(delay, units=units)
    assert False, "Simulation timeout"

@cocotb.test()
async def my_first_test(dut):
    """Try accessing the design."""
    
    dut.i_A.value = 0
    dut.i_B.value = 1
    dut.i_rdy.value = 0
    
    c = cocotb.clock.Clock(dut.i_clk, 2, 'ns')
    await cocotb.start(c.start(start_high=False))
    await cocotb.start(timeout_thread(1000))
    await reset_thread(dut.i_reset_n)
    
    await cocotb.start(hs_send(
        #  000110110
        # +101111001
        # ----------
        # 0110101111
        [
            (0,1),
            (1,0),
            (1,0),
            (0,1),
            (1,1),
            (1,1),
            (0,1),
            (0,0),
            (0,1)
        ],
        dut.i_clk,
        data = (dut.i_A, dut.i_B), vld = dut.i_vld, 
        rdy = dut.o_rdy, last = dut.i_last
    ))
    
    q = None
    ev = cocotb.triggers.Event()

    async def tricky_closure():
        nonlocal q
        q = await hs_recv(
            dut.i_clk,
            data = (dut.o_S, dut.o_overflow), vld = dut.o_vld, 
            rdy = dut.i_rdy, last = dut.o_last
        )
        ev.set()
    await cocotb.start(tricky_closure())

    print("Waiting to receive packet")
    await ev.wait()

    for thing in q:
        print(thing)