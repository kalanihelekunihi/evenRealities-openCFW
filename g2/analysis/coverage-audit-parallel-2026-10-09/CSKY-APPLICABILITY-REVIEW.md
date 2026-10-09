# C-SKY target applicability follow-up independently reviewed

The follow-up's concrete claims pass pinned-input review. [Verification](CSKY-APPLICABILITY-VERIFICATION.json), [discovery follow-up](../source-discovery-parallel-2026-10-09/CSKY-TARGET-APPLICABILITY-FOLLOWUP.md). Every successful acquisition/provider hash verifies; csky.c404remains explicitly failed evidence. No download, decoding, compilation, instruction execution or campaign update was performed.

At binutils32f97f3473656ee5d64e8e8c01a6006312c5828a, opcode declarations gate BNEZAD0xe8200000on CSKYV2_ISA_3E3R2and MULA.32.L0xf8008440on CSKYV2_ISA_3E3R1. Assembler CK803R3includesR1/R2/R3; CK804includes base803plus803R3. Thus the pinned assembler permits both instructions for CK804's feature mask. Base CK803alone does not prove either revision extension. This proves assembler eligibility, not target silicon features or execution semantics. The earlier manufacturer BNEZAD decrement-and-positive-branch correction remains necessary; opcode presence does not change it.

The existing NationalChip KWS Makefile independently verifies csky-abiv2-elf prefix (line190), exact ToolsV3.10.15/B20190929/GCC6.3.0version gate (230–231), CK804EF compile and assembly (237–241), and ck803/hard-fp library lookup (309–310). Therefore interpreting the runtime-directory name as proof of a physical CK803 CPU is invalid. The same authentic SDK requests CK804EF. SDK source is a configuration candidate, not proof the locked firmware used this SDK/compiler.

Vendor GCC1e9b70447a8417f5c692370de4533e43d754e8fa csky.h227–230explicitly says the published V2 ABI's stack alignment is incorrect and sets STACK_BOUNDARY32bits, four bytes. This is direct vendor compiler evidence contradicting the manual's eight-byte statement; it is not an inferred alignment optimization. It must qualify any unconditional eight-byte compiler requirement. It does not prove this later GCC policy was used by the SDK's6.3compiler or locked firmware.

Precise additive corrections needed, preserving originals:

- source-discovery-parallel-2026-10-09/CSKY-DESCRIPTOR-REFERENCES.md's manual excerpt is accurate as a quotation of the published document. Its eight-byte stack statement must be labeled disputed by the pinned vendor implementation, not treated as an unconditional producing-compiler contract.
- csky-descriptor-initializer-2026-10-09/SEMANTICS.md lines61–62 states that the official ABI requires eight bytes. Qualify this with vendor GCC's four-byte correction. An unchanged-SP function preserves its incoming alignment and proves neither an eight-byte caller requirement nor actual incoming SP alignment.
- coverage-audit-parallel-2026-10-09/DESCRIPTOR-SEMANTIC-CORRECTION.md paragraph3 carries the same eight-byte assumption. This review supersedes that unconditional compiler interpretation additively, without rewriting sealed evidence.
- Any physical CK803 claim derived solely from ck803/hard-fp directory naming needs correction to SDK CK804EF selection plus unknown locked-target identity. Existing packets already retain CK803/CK804 uncertainty; no new physical CPU conclusion is warranted.

The pinned CALL_REALLY_USED_REGISTERS array corroborates volatile r0–r3/r12–r13/r18–r25 and preserved r4–r11/r16–r17/r15. r14/SPis fixed; the array's call-used value does not authorize treating it as a scratch register. Prior preserved-register compatibility findings survive. Descriptor positive8..0loop behavior, exact accessor/initializer bytes, twelve-byte stride and low32multiply-add interpretation are not invalidated by these corrections. Neither a complete descriptor structure nor arbitrary BNEZAD nonzero semantics becomes established.

Remaining applicability gaps: authenticated locked-firmware CPU identity/revision/configuration, actual producing compiler/ABI release, manufacturer GX8002core feature declaration, and target-specific instruction semantics/exception behavior. The current vendor compiler pin is not the authenticated stock compiler; a local13.0.1candidate and SDK6.3gate do not bridge that gap. Four-byte stack ABI is supported for this pinned vendor implementation, not universally proven for every historical C-SKY build. No campaign admission, accepted counter or whole-source exhaustion follows.

All original evidence and campaign state remain preserved. Only assigned audit outputs changed.
