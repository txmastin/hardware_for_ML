*------------------------------------------------------------
* Stable Leaky Integrate-and-Fire Neuron with Realistic Spiking
*------------------------------------------------------------

.param Rm=1Meg
.param Cm=100p
.param Vthresh=2.2
.param Vreset=0
.param Vinput=5
.param Rstim=1Meg
.param Tstop=10m

* Input current: Vin / Rstim = 5uA
Vin in 0 DC {Vinput}
Rstim in vmem {Rstim}

* Membrane integration path
Rleak vmem 0 {Rm}
Cmem vmem 0 {Cm} IC=0

* Threshold reference
Vth vth_node 0 DC {Vthresh}

* Smooth analog spike output for plotting or later synapse use
Bspike spike_out 0 V = '1 / (1 + exp(-(V(vmem) - V(vth_node)) / 0.01))'

* Binary threshold detection for reset logic
Breset reset_ctrl 0 V = 'V(vmem) > V(vth_node) ? 1 : 0'

* Behavioral reset current path (drains vmem when threshold crossed)
Greset vmem 0 VALUE = { V(reset_ctrl) * 1u }

* Simulation setup
.options INTERP RELTOL=1e-3 ABSTOL=1n VNTOL=1u GMIN=1e-12
.ic v(vmem)=0
.tran 1u {Tstop}

* Output probes
.print tran v(vmem) v(spike_out)

.control
  run
  plot v(vmem) v(spike_out)
.endc

.end

