*---------------------------------------------
* Analog LIF Neuron - Single Unit Test
*---------------------------------------------
.param Rstim=1Meg
.param Rleak=10Meg
.param Cm=100p
.param Vthresh=2.2

* Input DC current
Vin in 0 DC 5
Rstim in vmem {Rstim}

* Membrane integration path
Rleak vmem 0 {Rleak}
Cmem vmem 0 {Cm} IC=0

* Threshold voltage reference
Vth vth_node 0 DC {Vthresh}

* Spike detection (analog impulse)
Bspike spike_out 0 V = '10 * exp(-((V(vmem) - V(vth_node))^2) / 0.001)'

* Reset current sourced from spike output
Greset vmem 0 VALUE = { V(spike_out) * 1u }

* Simulation command
.tran 0.01ms 20ms
.control
run
plot V(vmem) V(spike_out)
.endc
.end

