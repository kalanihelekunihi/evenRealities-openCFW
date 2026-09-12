# G2 bootloader BL-006 tails 0x004264F6/0x00426CC4/0x0042784C/0x004279EE source closure

70 more of the retained `official_blob` bytes -- four single-exit,
call-free, branch-free, literal-free stock tails that survive as
unreachable bytes after entry-redirect-replaced heads -- are now
produced from reviewed MIT C through the component's
`in_place_leaves` mechanism. All four payloads compile
relocation-free under the reviewed Apple-clang Cortex-M55 leaf
flags and reproduce the authenticated stock bytes exactly, so
`expected.sha256` equals `stock.sha256` for every leaf.

| Tail | Bytes | Leaf symbol |
| --- | --- | --- |
| `0x004264F6..0x00426506` | 16 | `open_cfw_bootloader_mspi_irq_status_tail_4264f6` |
| `0x00426CC4..0x00426CCC` | 8 | `open_cfw_bootloader_clkgen_dualclock_term_tail_426cc4` |
| `0x0042784C..0x00427878` | 44 | `open_cfw_bootloader_cmdq_init_rem_tail_42784c` |
| `0x004279EE..0x004279F0` | 2 | `open_cfw_bootloader_cmdq_blockrel_term_4279ee` |

The single new source is
`components/bootloader/core_overlay/runtime_bl006_mspi_clkgen_cmdq_tails_4264f6.c`.
Each leaf carries the naked-assembly target body (explicit
instruction widths, so the integrated assembler reproduces the
stock encodings bit-for-bit) plus a portable C twin compiled for
the host behavior tests. The verifier is
`g2/tests/test_runtime_bootloader_bl006_mspi_clkgen_cmdq_tails.py`
(9 tests: stock-SHA authentication, byte-exact rebuilds,
relocation-free checks, overlay registration checks,
survey-verdict pins, a whole-image `bl`-caller sweep, and ctypes
host-behavior cases against independent inline oracles).

## Why leaves, not data

Same precedent as the 424AB2/4250E6 and 42647C/4278BC tail
clusters: these four spans are executable tails with no literal
loads at all, so there is no pool to name -- only behavior to
reconstruct. The `in_place_leaves` route (307 leaves now
admitted) is the established mechanism for exact in-place
behavior reproduction.

## Tail semantics (from anchored Capstone decode)

- L `0x004264F6` (MSPI interrupt-status remainder; r0 = index,
  r1 = out slot, r2 = register base; r4 head-owned, restored):
  `r0 = [base + (index << 12) + 0x204]; *out = r0; return 0`
  via `pop {r4}; bx lr`. The leading `adds.w` also writes APSR
  flags; flags are not part of any return contract and the host
  twin does not model them.
- M `0x00426CC4` (CLKGEN dual-clock-switch terminal tail;
  r1 = value, r4 = head-owned slot): `[(slot << 4)] = value;
  return 0` via `pop {r1, pc}`. The host twin takes the slot
  explicitly plus a host region modelling the target address
  window, so the (slot << 4) byte-offset shape is testable (same
  pattern as the command-queue termination tail).
- N `0x0042784C` (command-queue initializer remainder; r0 =
  input word, r1 = config, r2 = out slot, r4 = head-owned
  state): with S = *(state + 0x24),
  `acc = *in | *(S + 0x14); **(S + 0x10) = acc;
  **(S + 4) = cfg->u32[1]; **S = (cfg->u8[8] << 1) & 2;
  *out = state; return 0` via `pop {r4, r5}; bx lr`. Note
  S + 0x14 holds a word *value* (OR-ed in), while S + 0x10 /
  S + 4 / S + 0 hold pointers. The host twin keeps the
  state -> link thread but represents the link word as a native
  struct: the target's 4-byte slots at +0x00/+0x04 would overlap
  as 8-byte host pointers (this overlap crashed the first host
  test draft with ASan-confirmed SIGSEGV/SIGKILL, which is how
  the struct model was derived -- the naked target body was
  never in doubt and is byte-exact).
- O `0x004279EE` (command-queue block-release terminal return):
  a bare `bx lr`; r0 passes through from the replaced head. The
  host twin is the identity function.

Every span's stock SHA-256 matches the pin already recorded in
the whole-image retained survey (no survey edit needed).

## Deadness evidence

All four spans sit in regions the whole-image retained survey
(`g2/tools/analyze_g2_bootloader_bl006_retained_survey.py`)
grades `corroborated_unreachable_control_flow`, pinned by the
verifier importing the survey. A whole-image Capstone `bl` sweep
finds no caller of any of the four entries (linear-sweep
desynchronization inside data is noted in the test; the sweep
corroborates the survey verdict rather than standing alone).
The stock-internal branches that target into these tails (e.g.
the status head's `b #0x00426500`, the dual-clock head's
`b #0x00426CCA`, three init-head branches into `0x00427874`,
the release span's `b #0x004279EE`) originate in the replaced
head spans, whose source-owned bodies return/jump away in the
built image. No live traffic is claimed: the reconstructions
document dead bytes from reviewed source and pin the behavior
the replaced heads must cover.

## Deliberately excluded: 0x004264B0..0x004264BA

The retained 10-byte slice after the source-owned MSPI
interrupt-disable return starts mid-instruction: the authentic
stock stream holds a 32-bit ADD.W at `0x004264AE` spanning
`0x004264AE..0x004264B2` (`12 eb 00 32`), so the slice opens
with that instruction's second halfword. It cannot be framed as
a behavior-leaf entry and needs the data/fill route instead.
Follow-up for a later BL-006 turn (same standing as the
`0x00426C22`/`0x00426C70` terminal returns, whose survey verdict
is the weaker `no_control_flow_reference_found`).

## License and toolchain

The source is MIT (new openCFW code, no vendor text). The
overlay pins the reviewed Apple-clang Cortex-M55 leaf flags
(`-Oz -fno-jump-tables -fomit-frame-pointer -fno-builtin
-mno-unaligned-access -fropi`, `strict_relocation_contract`,
zero relocations) plus the standard linux-clang profile
(expected == stock == unrelocated SHA).

## Build and gate standing

- New verifier: 9/9 pass (`test_compiled_leaves_match_stock`,
  `test_no_bl_caller_of_any_entry`,
  `test_overlay_registers_leaves`, `test_stock_spans_unchanged`,
  `test_survey_grades_spans_unreachable`, four ctypes behavior
  tests).
- Neighbor verifier `test_runtime_bootloader_bl006_cmdq_irq_tails`
  still 11/11 pass.
- `build_component.py` for the bootloader overlay succeeds with
  the four leaves (15,240 overlay bytes at `0x00434478`).
- `make -C g2 bootloader-component` remains blocked at its
  `littlefs-snapshot` prerequisite by another lane's uncommitted
  `apollo_main` overlay change (untouched by this turn).
- `test_bootloader_core_overlay`
  `test_provider_contract_is_manifest_ready_and_hardware_free`
  was already red at turn start: its pinned region contract
  predates even the prior turns' uncommitted BL-006 admissions
  (no mention of the `42647C` tails) and the test file itself
  carries another agent's uncommitted edits; the drift spans
  regions far outside this turn's four spans. Left untouched
  for that lane; recorded here as pre-existing.

## Score

BL-006 moves from 1,572 to 1,642 of 5,892 source-owned bytes
(+70); 62 of the 77 survey regions are fully closed. Hardware
qualification stays blocked by unavailable physical evidence;
no hardware operation occurred.
