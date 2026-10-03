# Independent review 2285

**Result:** PASS_SCOPED.

Isolated replay regenerated all 144 fixtures. Source, body [0x5CAC,0x5CF4), literal 65535 at [0x5CF4,0x5CF8), and candidate artifact hashes match. Decode confirms the bit-3 gate on the pointed row parameter, zero initialization of the stack output, child arguments (row index, halfword at row+128, zero, context as fifth stack argument), unsigned saturation to 65535, fresh pointer reload and halfword store at parameter+4. The child status remains in R0 through the tail and is asserted on the enabled path; disabled paths return zero. R4/SP checks pass.

**Limits:** All 144 cases use a controlled 7BC0 child and indices 0–2 with selected flags/slot/output/status values. No index validation exists in this body. Child semantics, aliasing, pointer faults, concurrency and physical meaning remain unresolved; no canonical admission.
