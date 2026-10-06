# Independent review P2-18507

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 120-byte interval `0x460898..0x460910`; instruction/reference manifests match. It inherits the 64-byte frame and header fields from the prior map. The `0x43CE9E` continuation call at entry uses the low byte of header R5 plus the prior diagnostic locals. It then tests low8(R5) for zero, followed by low16(R6) for exactly 3. On the exact-3 route, R5 is replaced with `R7+4`; comparison loads the halfword at R5+4 first and the word at R5 second. Equality branches to the external match route.

On mismatch, a fresh flag result controls diagnostic behavior. The bit-1 path reloads word[R5] then half[R5+4] (reverse of comparison order), writes those values plus literal/422 to SP12/SP8/SP4/SP0, and calls `0x43D574`. Subsequent bit checks use separate fresh `0x43D0CE` calls. The bit-2 route reloads word[R5] into SP0 and half[R5+4] into R3, then calls `0x43CE9E` with the recorded arguments. These are fresh field observations rather than reused comparison values; all SP writes are local-frame writes.

The map ends before the shared continuation/epilogue. Child contracts and later routes remain unresolved. Partial/unaccepted only.
