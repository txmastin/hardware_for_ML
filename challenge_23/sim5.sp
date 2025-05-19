* Fractional-Order LIF Neuron with RC Ladder (ngspice)

* --- Simulation Parameters ---
.param PI = 3.14159265359
.param alpha = {0.8}
.param stages = {5}
.param C0 = {1e-9}
.param flow = {0.1}
.param freqh = {1e4}
.param ratio = {(freqh/flow)**(1/(stages-1))}
.param R1 = {1/(2*PI*flow*C0*(ratio**((1-alpha)/2)))}
.param C1 = {C0*(ratio**((alpha-1)/2))}

* Calculate Rs and Cs
.param Rs[0] = {R1*(ratio**(0*(1-alpha)))}
.param Rs[1] = {R1*(ratio**(1*(1-alpha)))}
.param Rs[2] = {R1*(ratio**(2*(1-alpha)))}
.param Rs[3] = {R1*(ratio**(3*(1-alpha)))}
.param Rs[4] = {R1*(ratio**(4*(1-alpha)))}

.param Cs[0] = {C1*(ratio**0)}
.param Cs[1] = {C1*(ratio**1)}
.param Cs[2] = {C1*(ratio**2)}
.param Cs[3] = {C1*(ratio**3)}
.param Cs[4] = {C1*(ratio**4)}

.param Iin_amp = {3e-6}  ; Increased input current
.param Rleak = {500e3}
.param Vth = {0.5}
.param Ireset_amp = {50e-6} ; Use amplitude for current source
.param Tstop = {0.05}  ; Increased simulation time
.param dt = {1e-6} ; Suggest a smaller dt for SPICE if needed
.param Roff = {1e6}
.param Ron = {1}

* --- Circuit Elements ---
* Input Current Source
Iin 0 membrane {Iin_amp}

* Leak Resistor
Rleak membrane 0 {Rleak}

* RC Ladder Stages
R1 node_0 membrane {Rs[0]}
C1 node_0 0 {Cs[0]}
R2 node_1 node_0 {Rs[1]}
C2 node_1 0 {Cs[1]}
R3 node_2 node_1 {Rs[2]}
C3 node_2 0 {Cs[2]}
R4 node_3 node_2 {Rs[3]}
C4 node_3 0 {Cs[3]}
R5 membrane node_3 {Rs[4]}
C5 ladder 0 {Cs[4]}

* --- Spike Generation and Reset (Using Voltage-Controlled Resistor) ---
* Threshold Voltage Reference
Vth_ref vth_ref 0 {Vth}

* Comparator (Behavioral Voltage Source - output 0 or 1)
Ecomp control_node 0 VALUE = { V(membrane) > V(vth_ref) ? 1 : 0 }

* Voltage-Controlled Resistor for Reset
Rreset membrane 0 VALUE = { V(control_node) > 0.5 ? Ron : Roff } ; Low R when spiking

* Reset Current Source (Connected when Rreset is low)
Ireset_src membrane 0 {-Ireset_amp} ; Corrected syntax: no space before negative sign

* --- Initial Condition ---
.ic V(membrane)=0 V(node_0)=0 V(node_1)=0 V(node_2)=0 V(node_3)=0 V(ladder)=0

* --- Simulation Control ---
.tran {dt/10} {Tstop} 0 {dt/100} ; Smaller step for potentially better accuracy

* --- Output ---
.print TRAN V(membrane) V(control_node) I(Ireset_src)
.plot tran V(membrane) V(control_node) I(Ireset_src)*1e6 ; Plot reset current in uA
.end
