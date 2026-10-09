# C-SKY descriptor initializer review

Decision: byte accounting/mapping and decoder-backed candidate semantics supported; vendor-manual semantics/formal ABI and campaign admission remain open. [DESCRIPTOR-VERIFICATION.json](DESCRIPTOR-VERIFICATION.json) independently verifies four direct input pins, exact body hash and payload bytes. The 124-byte extent partitions 114 code +2 BKPT+8 literals with no gap; literal words are `0x20027350` and `0x004100FF`.

Conditional base maps `[0x102058D4,0x10205950)` to child `[0x28D0,0x294C)` and payload `[0xEE60,0xEEDC)` using complete-child start0xC590. Return at0x10205944 ends the ordinary code path; trailing0x0000 is not executed by that return, and the two literals are data. Do not count124 function-code bytes. Adjacent offset256 packet ends exactly at entry; prior campaign body at0x10205950 starts at extent end. Regex ownership scan remains supporting evidence, not global admission.

## Arithmetic and loop evidence

Pinned binutils `opcodes/csky-opc.h` maps BNEZAD opcode0xE8200000 and MULA.32.L opcode0xF8008440 with operand fields agreeing with displayed r18 and r13/r0/r23 operands. It establishes encoding, not execution semantics. Repository language definitions supply explicit semantics:

- `third-party/tools/ghidra-csky/C-SKY/data/languages/32b_branch.sinc:24`: decrement register, then branch if resulting register is nonzero.
- `.../32b_dsp.sinc:43`: zero-extend operands, multiply in64 bits, add zero-extended destination, assign low32 bits back to destination.

These corroborate eight iterations from initial r18=8 and descriptor offset `row*144 + slot*12` modulo32 bits. Signed versus unsigned multiplication has identical low32 result here; no saturating/high-half operation is indicated. Outer r1 starts0, increments and compares10; row byte offset r12 independently increments144. Row base/pointer sequence, mask to bits0–27, control words128+slot with bit16, terminal0x10088 and row+16 literal stores match the proposed interpretation. Candidate terminology “12-byte descriptors” describes stride, not a complete field layout: only two words per stride are written. Third word, memory purpose and external consumers remain unknown.

The language definitions are repository decoder models, not independently authenticated vendor instruction documentation or a hardware execution test. The vendor ISA PDF exists locally, but pdftotext and Python PDF readers were unavailable; workspace dependency lookup was unsupported for this thread. No packages were installed and no instruction experiment was duplicated. Consequently this review does not claim vendor-manual confirmation, flags/exception completeness or original execution. Owner should bind primary ISA excerpts before formal semantic admission if required by its contract.

## Caller ABI

The pinned complete-XIP caller at0x10205D20 follows root-field stores and calls this fixed-root initializer without preparing conventional arguments. After return it uses preserved r5 (zero) and r4 (global root), then calls another helper. The initializer does not modify r4/r5/r15, consistent with this observed dependency. It does modify r0–r3,r12,r13,r18,r19 and r20–r25 without a prologue; formal preservation rules for the extended ABI must be checked before assigning a conventional C function contract. Return r0 remains8 on the candidate path, r1=10, r12=1440 and r18=0; the caller does not consume returned r0 before overwriting it. Void is a caller-local interpretation, not evidence of a globally established prototype.

## Admission

Retain partial until exact ISA/flag behavior and needed ABI contract are validated; preserve mapping uncertainty and unknown global purpose. Bind stable function identity, complete instruction/edge correspondence, primary or validated decoder semantic evidence, caller context and independent review hashes in coordinator adoption records. Classify code/BKPT/literals separately, preserve shared adjacent ownership, and serialize coverage admission. No physical mapping, execution count, source-family identity, higher-level descriptor role or gate completion follows from this packet.

No packet, source, state, index or device mutation occurred; only additive audit output was written.
