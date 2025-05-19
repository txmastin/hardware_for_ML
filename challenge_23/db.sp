* Simple RC Circuit for Debugging

* --- Simulation Parameters ---
.param Tstop = {0.01}
.param dt = {1e-3}

* --- Circuit Elements ---
Vin 1 0 DC 1
R1 1 2 1e3
C1 2 0 1e-6

* --- Simulation Control ---
.tran {dt} {Tstop} 0 {dt/10}
.print TRAN V(2)
.plot tran V(2)
.end
