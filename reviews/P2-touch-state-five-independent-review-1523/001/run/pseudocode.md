# State-five preparation at 6A80

The56-byte body [6A80,6AB8) is followed by two literals. Resolve the peripheral through descriptor/configuration pointers, call685C(descriptor), then write0 to peripheral400. For three rows at64-byte stride, write03000000 at608 and literal00101000 at60C. The helper status is overwritten: return incidental03000000 inR0 and restore8-byte frame.

Nine original-instruction fixtures check seven orderedMMIOwrites, callargument, independence fromcontrolledhelperstatus, incidentalreturn andframe. 685C andphysicalhardware effects remain unresolved;MMIO is synthetic. No canonical admission or C implementation.
