# Authenticated C-SKY startup pass

Status: partial, ready for independent review of the instruction findings and tool defect. Four bounded bodies cover 244 unique instruction bytes. This is local P2 evidence; callee effects, hardware register effects, external delivery, full image coverage and gate acceptance remain open.

## Identity and coordinates

`authentication-and-bodies.json` rechecks the locked whole bundle, codec payload, canonical image hashes and exact codec-payload slices. Each body has a byte hash, child-file span, codec-file span and conditional runtime span. The stage1 transform is `runtime = child + 0x0fffffe8`: child offset 0xae4 corresponds to 0x10000acc. This is the intended 24-byte-header-subtracted coordinate model corroborated by the prior mapping audit, not measured resident ROM delivery. The G1 route still omits this transform; its correction needs coordinator review. Stage2 has `runtime = child + 0x10023400` on the reviewed conditional normal-NOR-copy route.

| Body | Conditional runtime span | Child span | Codec span | Bytes |
| --- | --- | --- | --- | --- |
| stage1 startup wrapper | [0x10000acc,0x10000af4) | [0xae4,0xb0c) | [0xa070,0xa098) | 40 |
| stage2 reset | [0x10023500,0x1002351e) | [0x100,0x11e) | [0x15514,0x15532) | 30 |
| stage2 clear BSS | [0x10023528,0x10023540) | [0x128,0x140) | [0x1553c,0x15554) | 24 |
| stage2 system setup | [0x1002354c,0x100235e2) | [0x14c,0x1e2) | [0x15560,0x155f6) | 150 |

The JSON receipt is the authoritative numerical record. Raw native listings also contain neighboring literal pools decoded as instructions by `-D`; those rows are not admitted executable bodies.

## New bounded semantics

The stage1 wrapper saves LR in one 32-bit stack slot, calls 0x10000a04, 0x10000f14, 0x1000092c and 0x10000134 in that order, sets r1=0 and r0=1, then calls 0x10000f04. It reads the 32-bit literal at 0x10000af4 (`0x20001280`), reads the word at that pointed address, and calls 0x10000a2c only when this word equals 2. The terminal pop restores LR, releases the four-byte stack slot and returns. GNU objdump and Ghidra agree on the body boundary. SDK `spl.c:spl_board_init_r` corroborates provisional names: `spl_boot_info_init`, `spl_board_init`, `spl_clk_init`, `spl_clear_bss`, `serial_init(1,0)`, then NOR image load. `spl.h` independently enumerates NOR as 2. The source's generic switch collapses to the observed NOR-only comparison, consistent with CONFIG_BOOT_BY_FLASH; no other build configuration is thereby proved.

Stage2 reset writes PSR=0x80000200, reads CHR then clears bit 3 and writes CHR, sets SP=0x2002f7fc, calls 0x1002354c then 0x10026314, and loops forever at 0x1002351c if the second call returns. SDK `start.S` matches this ordered startup skeleton and identifies candidate callees `system_init` and `main`. The following BKPT at 0x1002351e is outside the normal reachable body and cannot be used to claim breakpoint behavior recovered.

`clear_bss` saves/restores r4-r6 and writes zero in four-byte steps from 0x20026d80 to, but excluding, 0x2002ecec. The comparison is unsigned. The cleared interval is 0x7f6c (32,620) bytes, exactly 8,155 aligned words. If start >= end, the store loop is skipped. It returns through LR, and the following two BKPT words lie outside its body. `start.S:clear_bss` independently matches every operation.

System setup at 0x1002354c reads CAPR (CR19), PACR (CR20), PRSR (CR21), selects MPU region 0 by clearing PRSR bits 0..2, clears PACR base bits 12..31, sets size bits 1..5 to 31, sets PACR enable bit 0, and writes CAPR=(old_CAPR & 0xfefffcfe)|0x300. It ORs CCR (CR18) with 3. Source `core_ck804.h` identifies the register layouts and `system.c` matches region 0/base 0/4GB and both-mode RW configuration. It calls 0x10025a88, calls 0x10024984 and clears BSS only if that call returns 0, then calls 0x10025cbc. These align with candidate `clk_init`, `gx_pmu_get_start_mode` and `board_init`. It writes VBR=0x10023400; writes 0xff to 0xe000ec10; interleaves zero writes at 0xe000e300, e304, e308, e30c with 0xffffffff writes at 0xe000e280, e284, e288, e28c; then executes `psrset ee,ie` and returns. This ordering matches `system_vic_init` source. Silicon effects, callee bodies and exception semantics remain separate obligations.

## Second confirmed processor defect

The previously corrected MOVIH processor was used unchanged for the first authenticated pass. That exposed a distinct MFCR destination bug: `mfcr r1,chr` at 0x10023506 emits only `unique COPY chr`, leaving r1 unwritten. The CAPR/PACR/PRSR/CCR reads repeat the problem. In upstream `32b_priv.sinc` the constructor declares operand `i32_r_rz` but assigns `i32_c_rz`; Ghidra treats the latter as a temporary. The SDK inline assembly uses an output-register constraint (`=r`) for MFCR, while GNU independently decodes the same concrete destination register. These three sources establish the defect without relying on the new decompiled C.

`mfcr-destination.patch` changes only that assignment to `i32_r_rz`. `validate_mfcr.py` compiles the worker-owned complete private installation and imports the authenticated stage2 image into two fresh private projects. It requires the corrected P-code to write r1 from CHR and r2 from CAPR, and preserves both raw exports and processor hashes. Existing installed tooling and the prior worker's private installation remain unchanged.

The raw C export is still insufficient as reviewed pseudocode: control-register effects can disappear in ordinary decompiler C; literal-pool words appear as mutable globals in these no-autoanalysis imports; unknown function prototypes invent register parameters. The P-code and native instructions are required alongside manual register/MMIO descriptions. Ghidra prints INS as size-minus-one plus offset, while GNU prints end-bit plus start-bit: e.g. Ghidra `ins r3,r0,0x13,0xc` corresponds to GNU `ins r3,r0,31,12`. This is an operand presentation difference, not a second INS semantics defect.

## Tool receipts and finite next frontier

`receipts.json`, `followup-receipts.json` and `mfcr-fix-receipt.json` preserve actual commands, exit status and output hashes. Initial Ghidra execution lacked JAVA_HOME; replay with the prior validated OpenJDK 21 path succeeded. All four initial Ghidra decompiles succeeded and body extents agree with native disassembly. This says nothing about semantic completeness. Scripts import into named fresh projects; select new names before replay to preserve old outputs.

Ghidra-MCP discovery returned only the existing GUI `SyntheticSmoke` instance (PID 58627, TCP 8089), not these worker-private projects. No bridge context switch or import into that unrelated project was made. Standard headless export already obtained the required bounded evidence. A dedicated private bridge remains a possible convenience, not a source of missing runtime facts.

The finite immediate analysis frontier is the stage1 callees 0x10000a04, 0x10000f14, 0x1000092c, 0x10000134, 0x10000f04 and 0x10000a2c; the stage2 callees 0x10025a88, 0x10024984, 0x10025cbc and 0x10026314; plus independent review of these four records. Existing SDK provides strong function-name and control-register-layout shortcuts for those passes. No new source download was required in this worker scope. Resident stage1 header stripping/selection, DRAM-to-IRAM delivery/visibility, actual PMU mode and helper success remain external premises. The public-source frontier is not globally exhausted by these four bodies.
