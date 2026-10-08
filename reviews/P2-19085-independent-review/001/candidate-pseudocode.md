# Byte setter 0x4691BC..0x46921C

Partial/unaccepted; complete 96-byte function. PUSH R2/R3/R4/LR creates 16-byte frame, SP0 original R2 and SP4 original R3. R4=original R0. Call 0x46B44C with live original arguments. FULL child result nonzero: truncate R4 in place to low8(original R0); R1=1 if that byte nonzero else 0; store byte R1 at [child pointer+21]; branch shared return 0x46921A. Do not test the full original setter input.

FULL child result zero: fresh call 0x43D0CE with live arguments. If result bit1 set: SP4=literal 0x469B30; SP0=76; R3=literal 0x469B34; R2=literal 0x469B38; R1=literal 0x469B3C; R0=1 -> call 0x43D574. Separate fresh 0x43D0CE result bit0, or conditional third fresh result bit2, enables R1=literal 0x469B40, R2=R1, R0=0x04000000, live R3 -> 0x43CE9E. Otherwise skip.

Shared 0x46921A POP R0/R1/R4/PC consumes16 bytes. Therefore return R0 is original R2 on nonnull and null paths without bit1 diagnostics, or 76 when the bit1 diagnostic overwrote SP0. R1 similarly original R3 or diagnostic context literal. Child pointer/result does not survive into return R0. R4 restored. Child contracts unresolved; no gate, C or runtime claim.
