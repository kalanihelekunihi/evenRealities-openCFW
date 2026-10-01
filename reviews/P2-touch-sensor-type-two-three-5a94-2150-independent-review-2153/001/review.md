# Independent review 2153: Type-2/3 postprocessor at 0x5A94

**Result: PASS_SCOPED.** Candidate `analysis/touch-sensor-type-two-three-5a94-2150/001` remains unaccepted.

Independent Thumb decode confirms exact [0x5A94,0x5BA2) 270-byte body and continuous instruction extent. The listing and pseudocode agree on threshold arithmetic and item scanning, countdown/aggregate ordering, the two distinct constructor gates, scratch count consumption, ordered 8-byte copy calls, and restored saved registers/SP.

The isolated 864-fixture replay is byte-identical to the candidate. Fixture controls for 48CC/4A2A construct two entries and AA2C copy is intercepted; the checker does not establish those children’s general semantics. R0 is explicitly incidental, not a status contract.

Limit: Output construction and copy children are controlled; arbitrary scratch count, aliasing, concurrent mutation and physical sensor meaning remain open.
Limit: No canonical admission or C implementation.
