# LIS reset and FIFO-level getters C extraction

`lis2dw12_reset_get` at `0x757d2` and `lis2dw12_fifo_data_level_get` at
`0x753ac` now delegate their byte extraction and output write to shared C in
`native_lis_call_frames.c`. REA analysis and stock execution support both
changes. Each 26-byte native entry becomes a 12-byte frame bridge, with four
literal bytes and a twelve-byte descriptor. The common C body is 30 bytes
with the current compiler.

Both entries retain incoming R3 as a four-byte scratch word at entry SP-16.
The read uses its low byte, which remains the incoming seed if no data is
written. Reset extracts bit 6 of register 0x21; FIFO level extracts bits 0-5
of register 0x2f. Both always write the extracted byte to the caller's output,
including when the transport reports an error. The transport's full status
remains in R0; a 64-bit internal helper result also retains the extracted
value in R1. The public entry still has a 32-bit result. Its pop restores the
final scratch word into R3, including changes through an aliased output.

The ignored `build/goal-r1-lis-byte-getters/verify.py` probe passes 9,280
stock-versus-C scenarios: 4,640 per entry, including 64 null-output cases.
Actual transport wrappers execute on both sides. Cases cover every seed and
read byte, full-width statuses, successful and failing non-writing reads,
whole-word callback changes, all four scratch-byte output aliases and
unaligned external byte outputs. Checks include ordered context and scratch
accesses, callback arguments, output guards, R0/R1/R3, callee-saved registers,
SP, interrupt masks and eight-byte callback alignment. Null outputs reproduce
the unmapped byte write after the read, even on transport failure; complete
register equivalence at the fault is not claimed.

The other 21 function bodies in this compilation unit are unchanged. The
complete R1 build compiles 562 units without failures or duplicate strong
symbols. Imports remain 227 application and 34 bootloader. Exact source,
manifest, stock span, REA, integrated-source and probe bindings are in
[the machine-readable review](lis-c-byte-getters-review.json).

Final read callbacks are modeled. The C body adds callback stack depth while
preserving the native scratch address. These are partial C extractions;
physical reset/FIFO-level behavior, timing, complete fault-state equivalence,
final linking, provider qualification and byte identity remain unproven.
No G2 workflow gates or provider selections change.
