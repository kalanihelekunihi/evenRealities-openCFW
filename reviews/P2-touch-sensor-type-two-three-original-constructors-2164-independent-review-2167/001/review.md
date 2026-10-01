# Independent review 2167: Original type-2/3 constructors

**Result: PASS_SCOPED.** Candidate `analysis/touch-sensor-type-two-three-original-constructors-2164/001` remains unaccepted.

Independent Thumb decode confirms the exact 270-byte original 5A94 body and its boundaries; receipt, body and all artifact hashes match the pinned image. The 864-case isolated replay is byte-identical and runs original 5A94, 48CC, 4A2A, 49D4, AA2C and signed/unsigned division with no function interception.

The bounded cases assert full output buffer/count propagation, constructor gating by type/configuration, history count update, item and aggregate effects, copy ordering/arguments, R8 and SP. Type 2 with the tested equal nonzero items produces center position 50; zero-valued cases produce no entries. Type 3 bypasses the peak constructor as described.

Limit: The evidence is limited to the listed count/flag/timer/reload/delta/value/type/config combinations and initialized synthetic rows.
Limit: No physical sensor interpretation, arbitrary configurations, aliasing, concurrency, caller closure, canonical admission, or C implementation is claimed.
