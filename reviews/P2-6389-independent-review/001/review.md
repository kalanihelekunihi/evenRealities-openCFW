# Independent review 6389

Disposition: **PASS_SCOPED**; `accepted:false`.

Hashes match for both bodies at 0x42E2A2–0x42E2EA and 0x42E2EA–0x42E2F8. GNU Thumb decoding confirms the first routine's 16-byte save plus 16 local bytes (32-byte frame). It captures input R1 in R4, initializes R5=1, then uses register-shift LSL (`LSLS R5,R4`), which consumes the shift-count low byte; ARM register-shift semantics produce zero when the count is at least 32. It calls 0x41623A(input R0, 0x00800000), ignoring the result, then calls 0x416590(fresh literal-record+0x1C, mask R5, 1, 0x4E20). It tests `(result & mask) == mask`. A match leaves the child result in R0. A mismatch truncates R4 to a byte, stages that and the result plus a literal/tag 135, calls 0x4176CE(1, literals...), and returns the diagnostic child result. Since zero mask matches any result, the diagnostic is skipped when the low-byte shift count produces zero mask.

The function adds 20 to SP (discarding 16 local bytes and saved R3) then restores R4/R5/PC. The wrapper saves R7/LR, loads a literal-record+8 word, sets R1=1, calls the routine, then pops R0/PC; therefore wrapper return R0 is the wrapper's saved incoming R7, not the callee result.

No API purpose, hardware/runtime, C-equivalence, or admission claim is made. No canonical files or gates changed.
