# Application prefix with actual source selection

The bounded application prefix now executes A188 and both 9F44 source-switch calls, including actual 9F34. Both requests select the already-current source zero and return zero without writes. A188 input zero freshly replaces bits 5..4 in 40030028. Only the two 9C80 calls remain controlled inside the clock initialization wrapper. The later nine application dependencies remain controlled.

The original frequency source/divider chain and unsigned division execute at both 4734 calls. The fixture checks arrival at 3D50, descriptor insertion, interrupt enabling, previous register-write assertions and derived frequency RAM values. Initialized RAM and synthetic peripheral state are supplied. This is bounded original-instruction evidence; physical clock programming, timing, concurrent access and application loop behavior remain unresolved. No canonical admission or C implementation.
