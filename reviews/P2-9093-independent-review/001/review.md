# P2-9093 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 118 mapped instructions in the two builder routines match the pinned image.
- The 0x2021 builder requests a three-byte payload, writes low/high field bytes plus a data byte, dispatches only when allocation succeeds, and returns saved entry R3. The 0x2022 builder requests six bytes, writes three low16 fields, dispatches on nonnull allocation, returns null as zero, and otherwise returns child R0.

Limitations:

- No pointer validation or allocation/dispatch semantics beyond observed instruction flow; no concurrency, ownership, physical, or whole-firmware claim.
