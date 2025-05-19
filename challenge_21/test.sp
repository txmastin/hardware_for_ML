*-------------------------
* Fixed LIF Neuron Test
*-------------------------
.param Rstim=1Meg
.param Rleak=10Meg
.param Cm=100p
.param Vthresh=0.5

* Input current
Vin in 0 DC 5
Rstim in vmem {Rstim}

* Membrane
Rleak vmem 0 {Rleak}
Cmem vmem 0 {Cm} IC=0

* Threshold reference
Vth vth_node 0 DC {Vthresh}

* Smooth spike output
Bspike spike_out 0 V = '10 * exp(-((V(vmem) - V(vth_node))^2) / 0.001)'

.tran 0.01ms 20ms
.control
run
plot V(vmem) V(spike_out)
.endc
.end

