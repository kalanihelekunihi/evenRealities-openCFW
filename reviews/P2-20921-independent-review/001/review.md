# P2-20921 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for the 288-byte interval 0x47DB02..0x47DC22. Candidate and fresh instruction, pseudocode, and reference artifacts match, and the decoded instructions tile the range.

The entry saves 32 bytes, preserves entry R0 in R4, and returns 0 on a zero full result from the 47DA16 validation call. The subsequent word8 threshold is an unsigned comparison against 11. The first 474550 result is retained in R4; on its nonzero path, the 474870 result is compared signed against the literal threshold before the conditional 47498C/diagnostic calls. The later 474550 call is independent and replaces R4. Its zero path logs and joins cleanup; its nonzero path builds stack arguments from fresh words20/12 and a fresh word8, then calls the 512-byte helper. Both helper-result tests use signed `BLT` against 1. The subsequent record+24 helper call uses a fresh word12; its result is compared against another fresh word12, and mismatch logs with another fresh read. The 256-byte helper similarly uses a fresh word8 and a signed result test. The later output calls and diagnostic are followed by the shared cleanup.

At cleanup, word8 is saved, the `(record,4524,0,live R3)` helper runs, and the saved word8 is restored before explicit return 1. This covers both the missing-second-handle route and the normal output route. The final POP restores R1/R2/R3 from SP0/4/8, which may contain the original saved arguments or overwritten helper stack arguments. External helper contracts and literal-address ownership remain unresolved. No source or gate files changed.
