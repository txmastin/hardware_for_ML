*------------------------------------------------------------
* Robust LIF Neuron with Soft Thresholding and Safe Reset
*------------------------------------------------------------

.param Rm=1Meg
.param Cm=100p
.param Vthresh=2.2
.param Vreset=0
.param Vinput=5
.param Rstim=1Meg
.param Tstop=10m

* Input current source
Vin in 0 DC {Vinput}
Rstim in vmem {Rstim}

* Membrane RC path
Rleak vmem 0 {Rm}
Cmem vmem 0 {Cm} IC=0

* Threshold reference
Vth vth_node 0 DC {Vthresh}

* Sigmoid spike output: smooth, solver-friendly
Bspike spike_out 0 V = '1 / (1 + exp(-(V(vmem) - V(vth_node)) / 0.01))'

* Reset: controlled by spike_out, smoothly ramps on
Greset vmem 0 VALUE = { V(spike_out) * 10u }

* Simulation options
.options INTERP RELTOL=1e-3 ABSTOL=1n VNTOL=1u GMIN=1e-12
.ic v(vmem)=0
.tran 1u {Tstop}

* Outputs
.print tran v(vmem) v(spike_out)

.control
  run
  plot v(vmem) v(spike_out)
.endc

.end

