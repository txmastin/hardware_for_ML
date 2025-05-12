*------------------------------------------------------------
* Stable, Spiking LIF Neuron with Smooth Threshold and Hard Reset
*------------------------------------------------------------

.param Rm=1Meg
.param Cm=100p
.param Vthresh=0.7
.param Vreset=0
.param Vinput=5
.param Rstim=1Meg
.param Tstop=10m

* Input current
Vin in 0 DC {Vinput}
Rstim in vmem {Rstim}

* Membrane integration
Rleak vmem 0 {Rm}
Cmem vmem 0 {Cm} IC=0

* Threshold reference
Vth vth_node 0 DC {Vthresh}

* Smooth analog spike output (safe for plotting)
Bspike spike_out 0 V = '1 / (1 + exp(-(V(vmem) - V(vth_node)) / 0.01))'

* Soft binary reset control — fast sigmoid instead of hard step
Breset reset_gate 0 V = 'tanh((V(vmem) - V(vth_node)) / 0.01) > 0 ? 1 : 0'

* Reset path — hard constant current when reset_gate = 1
Greset vmem 0 VALUE = { V(reset_gate) * 10u }

* Simulation settings
.options INTERP RELTOL=1e-3 ABSTOL=1n VNTOL=1u GMIN=1e-12
.ic v(vmem)=0
.tran 1u {Tstop}

.print tran v(vmem) v(spike_out)

.control
  run
  plot v(vmem) v(spike_out)
.endc

.end

