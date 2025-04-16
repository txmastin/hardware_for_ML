from pymtl3 import *

class Neuron( Component ):
    def construct( s, width=16, threshold=1000, leak=10, rest=0, refrac_period=2 ):
        s.in_spike_sum = InPort( width )
        s.in_input     = InPort( width )
        s.fire_out     = OutPort( Bits1 )
        s.v_mem_out    = OutPort( width )

        s.refrac_count = RegRst( Bits3 )
        s.v_mem        = RegRst( Bits16 )

        @update
        def neuron_logic():
            if s.refrac_count.out > 0:
                s.refrac_count.in_ @= s.refrac_count.out - 1
                s.v_mem.in_ @= s.v_mem.out
                s.fire_out @= b1(0)
            else:
                new_v = s.v_mem.out * (100 - leak) // 100 + s.in_spike_sum + s.in_input
                if new_v > threshold:
                    s.v_mem.in_ @= rest
                    s.refrac_count.in_ @= refrac_period
                    s.fire_out @= b1(1)
                else:
                    s.v_mem.in_ @= new_v
                    s.fire_out @= b1(0)

            s.v_mem_out @= s.v_mem.out

