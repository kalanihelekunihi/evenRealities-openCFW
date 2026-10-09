# C-SKY target applicability follow-up

Prior descriptor manuals/index consulted first. No repeated PDF acquisition, firmware decode, compilation or campaign changes. Selected official C-SKY toolchain files acquired read-only under acquisitions/csky-target-contracts; exact URLs/pins/hashes/failures in provenance.json.

## Positive toolchain applicability constraints

Official c-sky/toolchain-build .gitmodules at `20c6b74f00ac3f464cb43ef2189a069d656933d5` references c-sky/binutils-gdb and c-sky/gcc, confirming the vendor dependency endpoints already used by repository build references.

Binutils pin `32f97f3473656ee5d64e8e8c01a6006312c5828a`:
- opcodes/csky-opc.h:4903–4907 defines BNEZAD opcode0xe8200000 gated by CSKYV2_ISA_3E3R2.
- opcodes/csky-opc.h:6009–6014 defines MULA.32.L opcode0xf8008440 gated by CSKYV2_ISA_3E3R1.
- gas/config/tc-csky.c:789–809 defines CK803 revisionsR1/R2/R3 as cumulative feature masks. CK804 includes CK803R3 and therefore bothR1 andR2 gates. CK803 base alone does not establish those revision features; -mcpu=ck804ef in authentic NationalChip SDK aligns with assembler support for both instructions.
- This is opcode/feature eligibility in the official assembler. It does NOT define instruction execution semantics or authenticate physical target revision/features. It complements, rather than replaces, previous manufacturer-manual semantics and exact firmware bytes.

Existing registered NationalChip KWS Makefile:190 uses csky-abiv2-elf prefix;230–231 explicitly gates C-SKY ToolsV3.10.15 Minilibc abiv2 B20190929/GCC6.3.0;237–241 requests -mcpu=ck804ef, hard float, little-endian assembly and ck804 symbol. Line309 uses a ck803/hard-fp library directory. Thus a ck803 runtime-directory label must NOT be promoted to a physical CK803 CPU claim: this same SDK requests CK804EF compilation. SDK settings support a provider/config candidate, not authentication that the locked firmware used this exact SDK/compiler.

## Important ABI correction

Vendor GCC pin `1e9b70447a8417f5c692370de4533e43d754e8fa`, gcc/config/csky/csky.h:227–230 explicitly states that the published V2 ABI document is incorrect about stack alignment, and sets STACK_BOUNDARY32bits (four bytes), not eight. The previous CSKY-DESCRIPTOR-REFERENCES.md correctly reported the published manual text but cannot serve as an unconditional compiler stack requirement. This additive follow-up preserves that evidence and records the contradiction/correction.

csky.h:519+ CALL_REALLY_USED_REGISTERS corroborates volatile r0–r3/r12–r13/r18–r25 and preserved r4–r11/r16–r17/r15; SP is fixed and must be handled by frame rules, not naively treated as a scratch register just because the call-use array marks it. This modern vendor compiler is not authenticated as the stock producing compiler (SDK gate references6.3; candidate local compiler13.0.1).

## Provenance/license and remaining limits

Binutils source notices GPLv3-or-later; pinned COPYING3 retained. GCC target files carry their own GPL notices. Toolchain-build .gitmodules provides dependency references; no LICENSE inferred for the entire scripts repository from that file. GCC csky.c URL at the pin returned404 and is recorded; only successfully acquired files are evidence. No compiler/emulator semantics or tests claimed.

Useful owner constraints: CK804 assembler feature support, CK803-version versus runtime-folder distinction, and four-byte compiler ABI alignment correction. Still missing: authenticated locked firmware CPU-ID/configuration or producing toolchain release, direct manufacturer GX8002 core feature declaration, and exact applicability of all decoder semantics to the target. No campaign admission change or universal public-source exhaustion claim follows.

Proposed optional reference submodules (not applied): https://github.com/c-sky/binutils-gdb.git at32f97f3473656ee5d64e8e8c01a6006312c5828a; https://github.com/c-sky/gcc.git at1e9b70447a8417f5c692370de4533e43d754e8fa. Prefer existing pinned repository build source references rather than adding duplicate large checkouts; sparse files here are comparison evidence, not registered submodules.
