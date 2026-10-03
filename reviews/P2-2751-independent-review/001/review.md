# Independent review 2751

**Result: PASS_SCOPED.** Static extraction verified all 215 instructions across `[0x4291EC,0x42944A)`. Source/body/artifact hashes match. The listing includes the PC-relative floating constant, unsigned wrapped fixed-byte delta conversion/multiply/truncation, packed return construction, low/high target writes, delay and poll sections, and control-gate operations stated in the map. The pool after the half-open body is excluded.

- This is a static map, not dynamic evidence of FP rounding or branch behavior.
- Wait/service, callers, hardware timing, and peripheral effects remain unverified.
- Private evidence only; no canonical admission.
