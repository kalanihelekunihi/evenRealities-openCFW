# Independent review 2303

**Result:** PASS_SCOPED.

Isolated replay regenerated all 576 fixtures. Source, body [0x6384,0x6462), and file hashes match. Decode confirms the cached flag tests and signed parameter-byte path, controlled 6352/6294/623C call conditions and stores, and the original 6262 shift helper arguments. The minimum is sticky across rows: validity 1/10 sets it to 8; other values set status 1 without clearing the minimum. Flag low bits equal to 1 add the 6262 mask result. Counts below the minimum or above 4096 return 2048 immediately; otherwise the loop continues. Exact controlled-call/write ledger and R4-R11/SP checks pass.

**Limits:** 6352/6294/623C are controlled; only 6262 is original. The fixtures use a bounded set of flags, signed bytes, validity sequences, counts and shift offsets. Child mutation, pointer aliasing and physical field meaning remain unresolved. No canonical admission.
