# G2 bootloader BL-006 tails 0x0042799E/0x00427B90 source closure

58 more of the retained `official_blob` bytes -- two multi-entry,
branch-bearing stock interiors that survive as unreachable bytes
after entry-redirect-replaced heads -- are now produced from
reviewed MIT C through the component's `in_place_leaves`
mechanism. Both payloads compile relocation-free under the
reviewed Apple-clang Cortex-M55 leaf flags and reproduce the
authenticated stock bytes exactly, so `expected.sha256` equals
`stock.sha256` for each leaf.

| Tail | Bytes | Leaf symbol |
| --- | --- | --- |
| `0x0042799E..0x004279BE` | 32 | `open_cfw_bootloader_cmdq_alloc_rem_tail_42799e` |
| `0x00427B90..0x00427BAA` | 26 | `open_cfw_bootloader_cmdq_errresume_rem_tail_427b90` |

The single new source is
`components/bootloader/core_overlay/runtime_bl006_cmdq_alloc_resume_tails_42799e.c`.
Each leaf carries the naked-assembly target body plus a portable C
twin compiled for the host behavior tests. The verifier is
`g2/tests/test_runtime_bootloader_bl006_cmdq_alloc_resume.py`
(10 tests: stock-SHA authentication, byte-exact rebuilds,
relocation-free checks, six assembler-probe emission checks,
overlay registration checks, survey-verdict pins, a whole-image
`bl`-caller sweep, and ctypes host-behavior cases against
independent inline oracles).

## Why these spans need reviewed encodings

Unlike the earlier single-exit tails, both spans exit through
narrow unconditional branches into their replaced heads (the
relocatable object assembles at address 0, so far-absolute
mnemonic branch operands are rejected with "branch target out of
range"). Each out-of-span exit is spelled with its reviewed
16-bit encoding (`.inst.n`); the span-internal `bhs` names a
local label normally. Six in-source assembler probes prove the
reference assembler emits the identical bytes for an identical
branch at the identical offset (same precedent as the binary32
remainder tail's `.inst.w`):

| Probe | Offset | Emission | Stock exit |
| --- | --- | --- | --- |
| `probe_b_54_back` | -54 | `e5 e7` | `b 0x00427970` at `0x004279A2` |
| `probe_b_38_back` | -38 | `ed e7` | `b 0x00427984` at `0x004279A6` |
| `probe_bhs_2_fwd` | +2 | `01 d2` | `bhs 0x004279BA` (internal, local label) |
| `probe_b_76_back` | -76 | `da e7` | `b 0x00427970` at `0x004279B8` |
| `probe_b_60_back` | -60 | `e2 e7` | `b 0x00427984` at `0x004279BC` |
| `probe_b_30_back` | -30 | `f1 e7` | `b 0x00427B76` at `0x00427B90` |

A `b`/`bhs` to a `.`-relative expression was rejected during
probing (unconditional defaults to the 4-byte `b.w`; conditional
refuses to fold), so local-label probes plus `.inst.n` spellings
are the reviewed route. The byte-exact rebuild test pins every
emission; probe sections are discarded from the firmware image.

## Tail semantics (from anchored Capstone decode)

- K `0x0042799E` (allocator interior; head-owned frame in r4-r7,
  command count in r6; live replacement
  `open_cfw_bootloader_cmdq_alloc_block_42790a`): three entries.
  K1 publishes the buffer-start word (`slot[1] = frame[1]`,
  rejoins the head success path with r0 = frame[1]). K2 returns
  the allocator failure code 5 (head epilogue). K3 computes
  `t = base + ((idx + 1) << 3)` in unsigned 32-bit wrap and
  returns base (head success path) or 5 (head epilogue) on
  `t >= lim` (unsigned `bhs`). The host twin dispatches on an
  explicit entry selector and reports the rejoined head address
  class, because r4-r7 are head-owned.
- L `0x00427B90` (error-resume end; live replacement
  `open_cfw_bootloader_cmdq_error_resume_427b38`): L1 loops back
  into the head scan (`b 0x00427B76`, non-returning, no host
  path). L2 publishes the queue-address register value into the
  found entry, publishes the entry pointer into its register
  slot, clears prefix bit 25 (the command-queue ENABLED word the
  enable/disable/reset tails maintain), and returns 0 via
  `bx lr`. The host twin models L2 with explicit memory.

## Deadness evidence

Both spans sit in regions the whole-image retained survey
(`g2/tools/analyze_g2_bootloader_bl006_retained_survey.py`)
grades `corroborated_unreachable_control_flow`, pinned by the
verifier importing the survey (3 inbound branches each, all from
replaced-head spans). A whole-image Capstone `bl` sweep finds no
caller of either entry. No live traffic is claimed: the
reconstructions document dead bytes from reviewed source and pin
the behavior the replaced AmbiqSuite-adapted heads already cover.

## License and toolchain

The source is MIT (new openCFW code, no vendor text). The
overlay pins the reviewed Apple-clang Cortex-M55 leaf flags
(`-Oz -fno-jump-tables -fomit-frame-pointer -fno-builtin
-mno-unaligned-access -fropi`, `strict_relocation_contract`,
zero relocations) plus the standard linux-clang profile
(expected == stock == unrelocated SHA).

## Build and gate standing

- New verifier: 10/10 pass (`test_stock_spans_unchanged`,
  `test_compiled_leaves_match_stock`,
  `test_probes_emit_stock_encodings` (6 probes),
  `test_overlay_registers_leaves`, `test_survey_grades_spans`,
  `test_no_bl_caller_of_any_entry`, four ctypes behavior tests
  covering 4 wrap + 1 fail + 14 bounds + 5 epilogue cases).
- Neighbor verifiers still green: `bl006_cmdq_irq_tails`,
  `bl006_mspi_clkgen_cmdq_tails`, `bl006_tail_leaves`,
  `bl006_tail7_fragments`, `bl006_retained_survey` (all OK).
- `build_component.py` for the bootloader overlay succeeds with
  the two leaves (15,240 overlay bytes at `0x00434478`).
- `make -C g2 bootloader-component` remains blocked at its
  `littlefs-snapshot` prerequisite by another lane's uncommitted
  `apollo_main` overlay change (untouched by this turn).

## Score

BL-006 moves from 1,722 to 1,780 of 5,892 source-owned bytes
(+58); 71 of the 77 survey regions are fully closed. Six
regions (4,112 bytes) remain: the MSPI device-configuration,
PIO-mixed, public device-configuration, and control-dispatcher
tails (`0x0042423C`, `0x004248E2`, `0x00424E84`, `0x0042612C`),
the call-bearing blocking-transfer tail (`0x004263E0`, 108 of
112 bytes uncovered -- its three `bl` calls need a route the
relocatable object cannot encode), and the binary32/SPOT span
(`0x00427E54`). Hardware qualification stays blocked by
unavailable physical evidence; no hardware operation occurred.
