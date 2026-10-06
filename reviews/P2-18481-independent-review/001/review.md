# Independent review P2-18481

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 70-byte span `0x4603DE..0x460424`; the generated instruction and PC-reference manifests match. This is a continuation of the frame opened at `0x460374`. It stores word 250 at lookup pointer +12 and calls `0x43D0CE` with lookup pointer and live R2/R3. On its bit-1 route, it writes the literal at `0x460E10` to SP4 and 287 to SP0 before calling `0x43D574`; it does not overwrite SP8.

The subsequent flag decisions use separate fresh `0x43D0CE` calls. The bit-2-set route calls `0x43CE9E` with the stated literal and mask; the other reaches the epilogue directly. POP loads SP0/SP4/SP8 into R0/R1/R2 and returns through LR, so the observed return values depend on whichever prefix/continuation diagnostics wrote the aliased saved slots. A null lookup route from the preceding prefix skips the word store and these later mask calls.

This map ends before the next instruction; no later behavior, child contract, or overall return meaning is inferred. Partial/unaccepted only.
