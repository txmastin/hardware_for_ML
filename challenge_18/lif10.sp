*------------------------------------------------------------
* Leaky Integrate-and-Fire Neuron - Extra Reliable Version
* Using standard ngspice components with no exotic elements
*------------------------------------------------------------

* Basic parameters
.param Threshold=0.7  ; Threshold voltage
.param InputCurr=5u   ; Input current
.param tau=100u       ; RC time constant (R*C)

* Supply voltages
V1 vdd 0 DC 5
V2 vss 0 DC -5

* Input current source
Iin 0 vmem DC {InputCurr}

* Membrane capacitor and leak resistor
Rm vmem 0 1Meg
Cm vmem 0 100p IC=0

* Comparator circuit (simplified)
Vth th 0 DC {Threshold}
Rdiv1 vdd mid 10k
Rdiv2 mid vss 10k
Ecomp gate 0 TABLE {V(vmem)-V(th)} = (-1,0) (-0.001,0) (0.001,5) (1,5)
Rgate gate 0 10k

* Output spike generator
Rspike_in gate spike_in 1k
Cspike spike_in 0 1n
Einv spike_inv 0 spike_in 0 1
Eout spike_out 0 TABLE {V(spike_in)} = (0.5,5) (1.5,5) (2.5,0) (5,0)
Rout spike_out 0 10k

* Reset circuit using analog switch
S1 vmem 0 gate 0 SMOD1
.model SMOD1 SW(Ron=1k Roff=1G Vt=2.5 Vh=0.5)

* Simulation control - adjust for reliable convergence
.option RELTOL=1e-2 ABSTOL=1u VNTOL=10u GMIN=1e-9
.tran 1u 5m UIC

.control
  set ngbehavior=ps
  set noacct
  unset noglob
  run
  plot v(vmem) v(spike_out)/5+0.8
.endc

.end
