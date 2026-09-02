# G2 bootloader SPOT-manager trim-commit source closure

The former census boundary at `0x0042AEE8` cut through a four-byte `MSR
PRIMASK` instruction. The corrected function ends at `0x0042AEEC`; the
remaining four bytes are a literal. Both reviewed compilers reproduce the full
80-byte body after four authenticated provider relocations. Host tests cover
the pending/state register gate. Live critical-section and register behavior
is blocked by unavailable physical evidence.
