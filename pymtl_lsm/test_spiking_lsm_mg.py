from pymtl3 import *
from pymtl3.passes import DefaultPassGroup
from SpikingLSM64 import SpikingLSM64
import numpy as np

def to_fixed(val, scale=2048):
    return int(np.round(val * scale)) & 0xFFFF

def run_lsm_mg_test():
    N = 64
    width = 16
    scale = 2048
    window_size = 5
    learning = True

    # Load Mackey-Glass data
    with open("../datasets/MG/mgdata.dat.txt", 'r') as file:
        lines = file.readlines()
    mg = [float(line.split()[1]) for line in lines]
    mg = np.array(mg)

    dut = SpikingLSM64()
    dut.apply( DefaultPassGroup(textwave=True, linetrace=True) )
    dut.sim_reset()

    print("step | input | target | prediction | error")
    print("-----|--------|--------|------------|--------")

    for t in range(window_size, len(mg)-1):
        inp_val = mg[t - window_size]
        tgt_val = mg[t]

        inp = to_fixed(inp_val)
        tgt = to_fixed(tgt_val)

        dut.in_input  @= Bits16(inp)
        dut.in_target @= Bits16(tgt)
        dut.in_learn  @= Bits1(1 if learning else 0)

        dut.sim_tick()

        pred = dut.out_prediction.uint()
        pred_float = (pred if pred < 2**15 else pred - 2**16) / scale
        inp_float  = inp_val
        tgt_float  = tgt_val
        error = tgt_float - pred_float

        print(f"{t:4} | {inp_float: .3f} | {tgt_float: .3f} | {pred_float: .3f} | {error: .3f}")

if __name__ == "__main__":
    run_lsm_mg_test()

