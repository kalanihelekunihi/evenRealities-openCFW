# OpenCFW shortcut-theory source frontier, 2026-10-09

This integrates three independent GPT-6.1 Sol low-reasoning passes over public
third-party/dependency sources, Ghidra MCP, Ablation, and REA. It stays within
P2 analysis: no firmware source, campaign ledger, gate, installed processor,
or authenticated input was changed.

## New knowledge retained

1. Official Ambiq Zephyr revision
   `2e3474150a431d255394521b4da3fb149f3b4052` is now pinned at
   `third-party/reference/ambiq-zephyr`. Its Apollo510B EM9305 driver defines
   vendor opcode `0xFFF2` as an eight-byte local-supported-feature mask.
   Stock `HciVscUpdateNvdsParam` at `0x004B4C8A` sends length eight and writes
   `FF 7C 01 0F B8 19`. The official mask is exactly
   `FF 7C 01 0F B8 19 00 00`. The opcode, length, six-byte stock prefix, and
   reset-chain placement therefore supersede the historical NVDS label while
   retaining the original function name as provenance. The stock tail still
   needs an explicit initialized-buffer receipt before claiming all eight bytes
   are proved. This is protocol/schema correlation, not proof that the 2026
   Zephyr tree produced the locked firmware.
2. The installed C-SKY Ghidra processor has a real `movih` semantic defect:
   it shifts a two-byte temporary left 16 and therefore lifts `movih r3,0xa0a0`
   to zero. A private patch zero-extends first, compiles with Ghidra 12.1.4,
   and evaluates to `0xA0A00000`. The global processor and pinned source remain
   unchanged. Until a reviewed private processor is bound to campaign mappings,
   Ghidra/bridge constant propagation and emulation are not trustworthy across
   affected C-SKY instructions.
3. Ghidra MCP v7.0.0 is operational but its live instance contains only the
   unrelated `SyntheticSmoke` project. It adds fast bounded xref/type/P-code
   interrogation after private-project setup; it does not add a completeness
   oracle. The bridge is pinned at `third-party/tools/ghidra-mcp`.
4. Ablation is useful for independently bounded ARM/Thumb call discovery and
   candidate ranking. Its general dispatcher misidentifies ARC and C-SKY as
   x86-64; installed Capstone has no ARC decoder, and the fallback omits LIMM
   handling. REA admits x86/x64/ARM/ARM64 ELF targets only, so ARC/C-SKY fail
   before Ghidra selection. Both tools are pinned as reference submodules;
   neither removes the architecture-specific recovery boundary.

## Source acquisition and pins

| Reference | Pin | Role |
| --- | --- | --- |
| Ambiq Zephyr | `2e3474150a431d255394521b4da3fb149f3b4052` | EM9305 opcode, feature mask, sleep/CLKREQ/recovery comparator |
| Ghidra MCP | `9cc29c0f1efb6c63a7d6898c9a23aff39397f992` | bounded private-project query bridge |
| Ablation | `97e051b44d1ac8129b35556fe533e6e8b5338db2` | ARM/Thumb ranking and verified direct-call triage |
| REA | `7aa4d768eb15317a63a476431ed75bafec086033` | evidence-oriented orchestration for supported native formats |

All are shallow, `update = none` submodules. Their presence does not admit them
to the firmware production dependency graph.

## Current finite frontier

The source/tool discovery frontier is exhausted for the inspected public inputs:
the new Ambiq comparator was acquired; NationalChip, Cordio, Ambiq SDK 5.2,
Pigweed, DSP, TLSF, FlashDB, LZ4, touch PDL/CapSense, and registered runtime
families were deduplicated against current reports; latest REA adds no firmware
architecture support; and no new official EM9305 4.2 source, private IAR/Nema
implementation, producing compiler project, or resident-ROM source surfaced.

What remains is not another generic source search. It requires target-side work
or genuinely new unavailable evidence:

- reconcile codec child/runtime mappings, then run the corrected private C-SKY
  processor against authenticated bodies and independently review every affected
  instruction semantic;
- use Ghidra MCP/REA only on private, hash-bound ARM projects and compare results
  against existing instruction evidence;
- supply authentic EM9305 vendor-extension/timer sources, original compiler and
  per-file configuration, resident-ROM contracts, generated touch configuration,
  or private graphics/Nema sources if they become available;
- continue whole-artifact P2 pseudocode and byte-ledger review. This target-side
  coverage remains open and is not equivalent to a third-party discovery gap.

No cybersecurity classifier blocked any phase, so Daybreak Blue was not needed.
G2 remains `P2_EXECUTING`; G2 through G6 are not opened by this report.

## Evidence

- `../shortcut-source-gap-20261009-agent1/REPORT.md`
- `../shortcut-ghidra-mcp-20261009-agent2/report.md`
- `../shortcut-ghidra-mcp-20261009-agent2/fixed-receipt.json`
- `../shortcut-ablation-rea-20261009-agent3/REPORT.md`
- `../../research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/004b4c8a.c`
- `../../research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/00569b56.c`
- `../../../third-party/reference/ambiq-zephyr/drivers/bluetooth/hci/apollox_blue.c`
- `../../../third-party/reference/ambiq-zephyr/drivers/bluetooth/hci/em9305_ll_features.h`
