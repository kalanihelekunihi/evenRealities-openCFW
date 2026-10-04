# P2-9061 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 30 instruction bytes match the locked image, and both literal addresses resolve to the recorded error-word and callback slots.
- Input error zero bypasses all global accesses. Nonzero stores the input error, checks callback slot, then reloads both error value and callback pointer before indirect call. Return is saved entry R7 via POP, so child result is discarded.

Limitations:

- Callback code and error-word semantics are unresolved; slot is unchecked after the null test and can change before reload. No physical transport, concurrency, or whole-firmware claim.
