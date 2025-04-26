from pymtl3 import *
from pymtl3.passes.backends.verilator import *
from SpikingLSM64 import SpikingLSM64

def test_lsm():
    dut = SpikingLSM64()
    dut.apply( DefaultPassGroup(textwave=True, linetrace=True) )
    dut.sim_reset()

    for t in range(10):
        dut.in_input @= Bits16(50 if t % 2 == 0 else 0)
        dut.sim_tick()

