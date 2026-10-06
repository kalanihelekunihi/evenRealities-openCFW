# Independent review P2-18503

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 126-byte continuation `0x4607B0..0x46082E`; instruction/reference manifests match. It inherits the 64-byte frame and R7 buffer base. The initial calls use SP+20 as R0, SP as R1, and 16 as R2 for `0x439C04`; then R0=SP+20, R1=literal `0x460E1C`, and R2=retained R7 for `0x490120`. The low byte of the full second-child result controls success: nonzero branches to `0x460834`; zero starts fresh flag diagnostics.

The bit-1 route separately reads SP32, selects either that loaded value or the literal at `0x461350`, then writes the selected value at SP8, literal `0x461354` at SP4, and 408 at SP0 before calling `0x43D574`. The following mask path uses fresh `0x43D0CE` calls for bit 0 and conditional bit 2. Its `0x43CE9E` arguments use a second independent SP32 observation for R3 (or literal fallback `0x461350`), not the first selected R0. This distinguishes the two stack reads. SP32 is within the inherited local frame and may reflect prior child writes; no fixed initialization is assumed.

These child effects and overall routine behavior remain unresolved. Local writes occur after the result test, and continuations are outside this map. Partial/unaccepted only.
