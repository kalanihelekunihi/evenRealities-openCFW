# P2-21115 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4803C2..0x480434 (114 bytes); instruction/reference outputs match candidate. Five wrappers cover offsets 36, 40, 48, 52, and 56. The first wrapper alone narrows the two entry arguments to LOW8 and replaces live R2/R3 call arguments with callback address/table pointer. The remaining four wrappers pass their callback address and table pointer in R0/R1, preserving live R2/R3. Every callback has a separate table-word reload after the nonzero check, and returns full callback R0. POP R1,PC restores saved R7. No null-safe call, output initialization, or callback semantics inferred.
