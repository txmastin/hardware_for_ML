*------------------------------------------------------------
* Stable, Spiking LIF Neuron with Fixed Behavioral Sources
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

* Spike detection using voltage-controlled voltage source (avoids B source)
* Use TABLE for compatibility with all ngspice versions
Espike spike_temp 0 TABLE {(V(vmem) - V(vth_node))/0.01} = 
+ (-100,0.01) (-10,0.01) (-5,0.01) (-2,0.012) (-1,0.018) 
+ (-0.5,0.05) (0,0.5) (0.5,0.95) (1,0.982) (2,0.988)
+ (5,0.99) (10,0.99) (100,0.99)
Rspike_temp spike_temp 0 1k

* Scale to proper output voltage
Eout spike_out 0 spike_temp 0 1
Rout spike_out 0 1k

* Reset detection (binary output: 0 or 1)
Ereset reset_temp 0 TABLE {(V(vmem) - V(vth_node))/0.01} = 
+ (-100,0) (-1,0) (-0.1,0) (0,0) (0.1,1) (1,1) (100,1)
Rreset_temp reset_temp 0 1k

* Reset current source (10uA when reset active)
Gcurr vmem 0 VALUE={V(reset_temp) * 10u}

* Simulation settings - adjusted for stability
.options INTERP RELTOL=1e-3 ABSTOL=1n VNTOL=1u GMIN=1e-12
.ic v(vmem)=0
.tran 1u {Tstop}

.control
  set ngbehavior=ps
  set noaskquit
  run
  plot v(vmem) v(spike_out)
.endc

.end
