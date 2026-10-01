# Threshold flags at 623C

The 38-byte body [623C,6262) reads row halfword +44 and context byte +77 through descriptor word +8, then adds them as unsigned values. It calls original 6220 with context halfword +60. Threshold is (returned scale + 1) >> 2. Return 10 if the sum is at least threshold, otherwise 8. No persistent writes occur.

The 312 fixtures execute both original routines and check threshold boundaries, high scales, offsets, returned flags and frame restoration. The bit-scale helper has separate exhaustive halfword evidence in 1429. Pointer validity and physical field meanings remain unresolved. No canonical admission or C implementation.
