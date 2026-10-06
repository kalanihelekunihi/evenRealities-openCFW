# Independent review P2-18501

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 106-byte prefix `0x460746..0x4607B0`; instruction/reference manifests match. It inherits the 64-byte frame, with R4 as mode, R5 as length, and R6 as input. The full-word R4 gate is exact zero; nonzero branches to external `0x460D54`.

For mode zero, bit-1, bit-0, and conditional bit-2 decisions use separate fresh `0x43D0CE` calls. The first diagnostic path writes retained length at SP8, literal at SP4, and 403 at SP0 before `0x43D574`; another route calls `0x43CE9E` with R5 and its literal. The remaining branch prepares R1=892/R2=0 and loads a literal buffer pointer into R7/R4, replacing the prior mode value in R4, then calls `0x43C0E4` with live R3. Finally, it passes R0=SP, R1=retained R6, R2=retained R5 to `0x48F49C`, also with live R3.

No input null/length checks appear in this span. Stack locals may contain prior diagnostic writes; no transform semantics or initialized content is inferred. Continuation/epilogue remains outside. Partial/unaccepted only.
