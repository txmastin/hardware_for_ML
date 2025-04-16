from pymtl3 import *
from pymtl3.stdlib.basic_rtl import RegRst
import numpy as np

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

class SpikingLSM64( Component ):
    def construct( s ):
        N = 64
        width = 16
        scale = 2048
        spectral_radius = 0.9
        connectivity = 0.2
        learning_rate = 2  # Q5.11 fixed-point scale of 0.001

        # I/O
        s.in_input = InPort( width )
        s.in_target = InPort( width )
        s.in_learn  = InPort( Bits1 )
        s.out_spike_sum = OutPort( clog2(N+1) )
        s.out_prediction = OutPort( width )

        # Instantiate neurons
        s.neurons = []
        for i in range(N):
            neuron = Neuron(threshold=500, leak=5, rest=0)
            setattr(s, f"neuron_{i}", neuron)
            s.neurons.append(neuron)

        s.spike_vector = [ Wire(Bits1) for _ in range(N) ]
        s.activation_vector = [ Wire(Bits16) for _ in range(N) ]

        # Weight generation (fixed-point Q5.11)
        np.random.seed(42)

        W = np.random.rand(N, N)
        W[np.random.rand(N, N) > connectivity] = 0
        np.fill_diagonal(W, 0)
        max_eig = max(abs(np.linalg.eigvals(W)))
        W = W / max_eig * spectral_radius
        W_fixed = np.round(W * scale).astype(int)
        W_in_fixed = np.round(np.random.rand(N) * scale).astype(int)

        s.w_flat = [ Bits16(int(W_fixed[i][j])) for i in range(N) for j in range(N) ]

        s.W_in = [ Bits16(int(W_in_fixed[i])) for i in range(N) ]

        # Make W_out trainable in hardware
        s.W_out_regs = []
        initial_w_out = np.round((np.random.rand(N) * (np.random.rand(N) < connectivity)) * scale).astype(int)
        for i in range(N):
            reg = RegRst(Bits16)
            reg.reset_value = Bits16(int(initial_w_out[i]))
            setattr(s, f"w_out_{i}", reg)
            s.W_out_regs.append(reg)

        @update
        def compute_inputs():
            for i in range(64):
                acc = Bits16(0)
                for j in range(64):
                    acc += s.spike_vector[j] * s.w_flat[i * 64 + j]
                acc += (s.in_input * s.W_in[i]) >> 11
                s.neurons[i].in_spike_sum @= acc
                s.neurons[i].in_input @= Bits16(0)

        @update
        def update_spikes():
            total_spikes = 0
            for i in range(N):
                s.spike_vector[i] @= s.neurons[i].fire_out
                s.activation_vector[i] @= s.neurons[i].v_mem_out
                total_spikes += s.neurons[i].fire_out
            s.out_spike_sum @= total_spikes

        @update
        def compute_output():
            result = Bits32(0)
            for i in range(N):
                result += (s.activation_vector[i] * sext(s.W_out_regs[i].out, 32)) >> 11
            s.out_prediction @= result[0:width]

        @update
        def update_weights():
            if s.in_learn:
                error = sext(s.in_target, 32) - sext(s.out_prediction, 32)
                for i in range(N):
                    delta = ((error * sext(s.activation_vector[i], 32) * learning_rate) >> 11)[0:16]
                    s.W_out_regs[i].in_ @= s.W_out_regs[i].out + delta
            else:
                for i in range(N):
                    s.W_out_regs[i].in_ @= s.W_out_regs[i].out

