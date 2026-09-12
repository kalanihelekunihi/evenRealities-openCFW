# G2 bootloader BL-006 MSPI tails source closure (M/N/O/P/Q)

2,792 more retained `official_blob` bytes -- five dead MSPI
interiors that survive as unreachable bytes after
entry-redirect-replaced heads -- are now produced from reviewed
MIT C through the component's `in_place_leaves` mechanism. Every
payload compiles under the reviewed Apple-clang Cortex-M55 leaf
flags and reproduces the authenticated stock bytes exactly
(`expected.sha256` equals `stock.sha256` for each leaf;
relocation-bearing leaves resolve their reviewed relocations to
the same bytes).

| Tail | Bytes | Leaf symbol | Relocs |
| --- | --- | --- | --- |
| `0x004248E2..0x00424976` (M) | 148 | `..._mspi_piomix_rem_tail_4248e2` | 0 |
| `0x004263E0..0x0042644C` (N) | 108 | `..._mspi_blocking_rem_tail_4263e0` | 2 CALL |
| `0x0042612C..0x004262E0` (O) | 436 | `..._mspi_control_rem_tail_42612c` | 1 CALL |
| `0x00424E84..0x00425066` (P) | 482 | `..._mspi_devconfig_rem_tail_424e84` | 2 CALL |
| `0x0042423C..0x0042488E` (Q) | 1618 | `..._mspi_devconfig2_rem_tail_42423c` | 0 |

New sources (all MIT, each with a naked-assembly target body
plus a portable C twin for host testing):

- `runtime_bl006_mspi_piomix_tail_4248e2.c`
- `runtime_bl006_mspi_blocking_tail_4263e0.c`
- `runtime_bl006_mspi_control_tail_42612c.c`
- `runtime_bl006_mspi_devconfig_tail_424e84.c`
- `runtime_bl006_mspi_devconfig2_tail_42423c.c`

The verifier is
`g2/tests/test_runtime_bootloader_bl006_mspi_tails.py`
(12 tests: stock-SHA authentication, byte-exact rebuilds with
relocation-set checks, assembler-probe emission checks, decoder
verification of wide branch spellings, overlay registration
checks, survey-verdict pins, a whole-image `bl`-caller sweep,
and ctypes host-behavior cases against independent inline
oracles).

## Tail semantics (from anchored Capstone decode)

- M `0x004248E2` (PIO-mixed remainder; live head returns
  first): seven arms (E0-E6) writing one register nibble each
  (1, 3, 5, 7, clear, 9, 11) at `[base + (index << 12) + 4]`
  (E0 uses the incoming block + 4), then the shared
  `movs r0, #0; bx lr` epilogue. Pool words (notably
  `0x004251A4`) are reused through stock PC-relative offsets.
- N `0x004263E0` (blocking-transfer end; single fallthrough
  entry): mode dispatch on `[r1 + 6]` to the in-place FIFO
  read/write services (reviewed `R_ARM_THM_CALL` relocations),
  error restore of two words on nonzero results, otherwise the
  retained delay service at `0x0041D246` (reviewed `.inst.w`,
  see below), then register restore and a single `pop.w`
  return. The delay call's target stays retained under another
  work item, so no source symbol exists for it.
- O `0x0042612C` (control-dispatcher remainder; 8 entries,
  never returns): enable gate, descriptor validation, three
  register-configuration paths, and a constant failure stub;
  every arm rejoins a replaced-head join (`0x004252E6` /
  `0x004252E8`). One reviewed call relocation (in-place
  `cq_enable`); the pool word at `0x00426804` is reused
  verbatim.
- P `0x00424E84` (public device-configuration body; 13
  entries): full 0x90/0x94/0x98 control-word build from
  configuration/state bytes, divider programming with a reject
  path (returns 5), nine divider-select arms that OR a constant
  and rejoin the head, a fail stub, and a head-jump arm;
  returns 0/5 through the shared pop. Two reviewed call
  relocations (in-place `device_configure`, `xip_off_delay`;
  both results discarded by stock). The pool word at
  `0x004251B8` is reused verbatim.
- Q `0x0042423C` (device-configuration arms; 30 entries, 24
  arms in 4 sub-patterns, shared return-0 epilogue): per-arm
  nibble/constant programming at +0x84/+0x90/+0x44 with a
  descriptor-byte choice (P-A), constant 0x3FF (P-B/P-C), or
  pool-word publish (P-D, writing `0x0007FFFF`). The 39 pool
  loads reuse four retained pool words verbatim.

## Reviewed encodings: `.inst`, `.inst.w`, probes, and one divergence

The relocatable object assembles at address 0, so branches and
calls into replaced-head spans (or retained code) cannot name
far-absolute mnemonic operands ("branch target out of range").
Each such exit is spelled with its reviewed encoding; internal
branches name labels normally (unique Q-names in the
ten-target P block, where numeric locals miscompile alongside
the two `bl` relocations with undefined `.Ltmp`
temporaries -- the named form assembles byte-exact).

- Narrow unconditional/conditional exits (5 in the earlier K/L
  turn; 2 here in O; 10 in P): `.inst` spellings, each proven
  by an in-source probe emitting the identical bytes at the
  identical offset (binary32-tail precedent). The P probes
  cover 9 distinct encodings (the two -114 exits share one).
- The retained-target call in N (`bl 0x0041D246`, offset
  -37362, stock bytes `f6 f7 07 ff`): `.inst.w 0xF7F6FF07`
  (note: `.inst.w` takes opcode halves in reading order --
  first halfword high -- verified against the binary32
  precedent) plus a same-offset probe. An early draft used the
  miscomputed offset -331250; the probe emitted a
  self-consistent but wrong encoding, which the byte-match
  check caught and the corrected -37362 probe now pins.
- The eleven wide exits in O: `.inst.w` spellings pinned by
  DECODER verification instead of probes. The reference
  assembler emits a one-variant-bit different yet
  equally-correct `b.w` encoding than the stock toolchain for
  these offsets (verified: same offset at 4-aligned and
  2-aligned probe addresses both yield the variant; both
  variants disassemble to the documented target). The verifier
  decodes each spelled site and checks the branch target.

## Deadness evidence

All five spans sit in regions the whole-image retained survey
grades `corroborated_unreachable_control_flow`, pinned by the
verifier importing the survey (inbound branches all originate
in replaced-head spans). A whole-image Capstone `bl` sweep
finds no caller of any of the five entries. No live traffic is
claimed: the reconstructions document dead bytes from reviewed
source and pin the behavior the replaced AmbiqSuite-adapted
heads already cover.

One interaction: leaf Q's dead F3 arms load the retained pool
word at `0x00425168`, which an earlier turn's fragment test
pinned as loader-free. The stock loader always existed inside
this not-yet-reconstructed dead code; the leaf documents it
without executing it. That test now exempts in-place leaves
inside survey-graded unreachable spans (live-loader coverage
unchanged -- it still scans every live leaf), with this case
cited in its comment.

## License and toolchain

All five sources are MIT (new openCFW code, no vendor text).
The overlay pins the reviewed Apple-clang Cortex-M55 leaf
flags (`-Oz -fno-jump-tables -fomit-frame-pointer -fno-builtin
-mno-unaligned-access -fropi`, `strict_relocation_contract`,
exact relocation sets) plus the standard linux-clang profile
(expected == stock == unrelocated SHA).

## Build and gate standing

- New verifier: 12/12 pass (stock SHAs, 5 byte-exact rebuilds
  with relocation-set checks, 12 probe emissions, 11 decoder
  checks, registration, survey verdicts, `bl` sweep, and 5
  behavior groups: 21 nibble cases, 8 dispatch cases, 6+
  control cases, main/divider/fail/jump devconfig cases, and
  48 devconfig2 arm cases).
- Neighbor verifiers green after a one-line-class refinement:
  `bl006_tail7_fragments` 14/14 (loader scan now
  deadness-aware, above), plus `cmdq_irq_tails`,
  `mspi_clkgen_cmdq_tails`, `tail_leaves`, retained survey,
  and `cmdq_alloc_resume` all OK.
- `build_component.py` for the bootloader overlay succeeds
  with the five leaves (15,240 overlay bytes at `0x00434478`).
- `make -C g2 bootloader-component` remains blocked at its
  `littlefs-snapshot` prerequisite by another lane's
  uncommitted `apollo_main` overlay change (untouched by this
  turn).

## Score and remainder

BL-006 moves from 1,780 to 4,572 of 5,892 source-owned bytes
(+2,792); 76 of the 77 survey regions are fully closed. The
single remaining region is the 1,316-byte binary32/SPOT span
at `0x00427E54`, which the earlier survey scoped to a
dead-tail fill primitive (a shared builder change that does
not exist yet) or full SPOT-manager reconstruction with float
semantics -- explicitly out of reach for a leaf turn and left
as the precise followup. Hardware qualification stays blocked
by unavailable physical evidence; no hardware operation
occurred.
