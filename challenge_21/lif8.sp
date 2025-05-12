
* Leaky Integrate-and-Fire Neuron - Simple and Reliable Version
* Uses basic ngspice components with proven compatibility

* Basic circuit elements
Iin in 0 DC 0.2u        ; Input current (increased for faster spiking)
Rm in 0 10Meg           ; Leak resistor
Cm in 0 1n              ; Membrane capacitor
Vth th 0 DC 1.0         ; Threshold voltage reference

* Simple comparator using a voltage-controlled voltage source
Ecomp comp 0 in th 1000 ; High gain amplifier as comparator
Rcomp1 comp mid 1k      ; RC filter to clean up comparator output
Ccomp mid 0 1n
Eclip out 0 TABLE {V(mid)} = (-10,0) (-0.001,0) (0.001,5) (10,5) ; Clip to 0-5V

* Reset circuit using voltage-controlled switch
Vreset reset_src 0 DC 0 ; Reset voltage source (0V)
S1 in reset_src out 0 RESET_SW
.model RESET_SW SW(Ron=10 Roff=1G Vt=2.5 Vh=0.5)

* Analysis commands
.tran 1ms 500ms uic
.control
run
plot v(in) v(out)*0.2+1.2
.endc

* Initial conditions
.ic V(in)=0

.end
