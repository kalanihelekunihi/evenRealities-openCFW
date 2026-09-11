# G2 bootloader retained-gap census, `0x0042B9BA..0x00430470` (BL-009)

Status: read-only reconnaissance; no source landed, no overlay/manifest edit
Analysis mode: read-only; no signing, flashing, erase, or hardware operation

## Result

BL-009 assigns 25 disjoint `official_blob` spans totaling 5,978 bytes inside
the fully-reconstructed `apollo_bootloader` `core_overlay` (198 functions
already source-routed in this address range). Re-checking
`g2/build/source/flash-plan.json` on 2026-09-11 confirms all 25 spans are
still `official_blob`; none has been claimed since the work-item list was
generated.

Disassembling every span (Capstone Thumb/M-class, cross-checked against raw
bytes) gives three classes, not one:

- **Seven spans (≈4,556 bytes) contain executable Cortex-M55 Thumb-2 code**,
  not alignment filler: `0x0042B9BA` (1,078B, a ~1,010-byte function behind a
  ~68-byte leading literal pool), `0x0042BFA4` (144B), `0x0042D5C2` (650B),
  `0x0042E6F2` (434B, a real function with `push.w`/`bl` calls), `0x0042F14E`
  (122B, mostly a literal/pointer table with a short helper), `0x0042F3DA`
  (2,854B, the largest: real code followed by a ~200-entry sparse
  index→small-value table and a further block that does not resemble code or
  a simple table), and `0x004303DE` (146B, three near-identical 42-byte
  wrapper functions plus a short pointer tail).
- **Sixteen spans (≈1,166 bytes) are non-code data**: zero/alignment
  padding, small literal cells (register addresses, sentinels, timing
  constants), and one clear 192-byte pointer table (`0x0042E104`).
- **Two spans (4 bytes total) are unambiguous zero-fill alignment**:
  `0x0042E642..0x0042E644` and `0x0042FFFE..0x00430000`, each exactly `00 00`
  between two already-landed Thumb functions.

None of the 25 spans has been claimed, in-place-leaf or in-place-data,
by any other landed or in-progress work in this component as of this
census (`git status`/`overlay.json` cross-check).

## Why none of this closed this turn

Rule 2 in the standing work-item instructions excludes "binary bytes encoded
as C arrays" from counting as reconstruction, and rule 8 requires honest
verification. Two independent findings block a defensible close of any of
the seven code-bearing spans or the pointer-table span within this pass:

1. **The code spans require the same per-function rigor as the 198 already
   -landed neighbors** (disassembly-anchored control flow, ABI/stack
   modeling, literal identification, differential testing against the
   stock oracle) — each of the three largest (1,078B / 650B / 2,854B) is on
   the order of one dedicated BL-xxx item by itself, not a few-line patch.
2. **Every code span's call targets, and the pointer table's targets, chase
   into bytes outside BL-009's own range that are themselves still fully
   opaque and are already claimed by sibling work in progress**:
   - `0x0042B9BA`'s function calls `0x0041B8EC`; `0x0042E6F2`'s function calls
     `0x0041B3E4`/`0x0041B3FC`/`0x004166AA`/`0x004176CE`; `0x004303DE`'s three
     wrappers all call `0x0041DF48`/`0x0041DFC6`/`0x0041E09A`. All of these
     targets fall inside `0x0041B862..0x0041F918` (16,566 bytes), which
     `remaining-work.md` shows as **BL-005, in-progress** as of this pass.
   - The 192-byte pointer table at `0x0042E104` resolves 44 of its 48 words
     to addresses in `0x00433000..0x00434477`. That whole span is one
     contiguous 6,821-byte `official_blob` region
     (`0x004329D2..0x00434477`), shown as **BL-012, in-progress**. (A fifth
     neighboring span, `0x00431E70..0x004329C4`, is **BL-011, in-progress**.)
     Writing the table's literal pointer *values* today would be mechanical
     (the addresses are fixed regardless of whether the pointees are
     source-routed yet), but the goal text is explicit that "typed external
     -provider interfaces... that still call retained bytes" do not satisfy
     completion — a reconstructed table whose 44 entries still route into
     opaque code would move bytes from one ledger bucket to another without
     reducing opaque *functionality*, which is the actual bar.

Given that, this pass intentionally did not touch `overlay.json`,
`build_component.py`, or any manifest, and took no integration lock — there
is nothing to place yet that would be honest, verified production routing.

## Per-span classification

All addresses are `0x0042xxxx`/`0x0043xxxx` (bootloader run base
`0x00410000`); "class" is the disassembly-anchored finding, not the original
work-item label.

| Span | Bytes | Class | Notes |
| --- | ---: | --- | --- |
| `0x0042B9BA..0x0042BDF0` | 1,078 | code | ~68B leading literal pool, then a real function from `0x0042BA00` (`push.w {r4-r8,sb,sl,lr}`) to `0x0042BDF0`; calls `0x0041B8EC` (BL-005 range) |
| `0x0042BF4E..0x0042BF54` | 6 | data | 2B zero pad + `0xE000ED14` (Cortex-M `SCB->CCR`) |
| `0x0042BFA4..0x0042C034` | 144 | mixed, mostly data | Capstone decodes mostly non-code opcodes across the span; boundary between literal cells and any real helper is undetermined |
| `0x0042C6E4..0x0042C6F8` | 20 | data | words `0x0`, `0x40050000` (Apollo peripheral base-address shape), `0x08000001`, `0x08000002`, `0xDEADBEEF` (sentinel) |
| `0x0042C980..0x0042C988` | 8 | data | two words, `0x05B8D800` / `0x0003D090`; no identified owner |
| `0x0042CDB0..0x0042CDF8` | 72 | data | mixes SRAM pointers (`0x2001455C`), a repeated `0x40050000` peripheral base, `0xFFFFFBFE`, decimal-round constants `0xF4240`/`0x186A0`/`0x61A80` (1,000,000 / 100,000 / 400,000 — clock/baud shape), and three two-word records sharing a `0x2301` low tag |
| `0x0042D0F2..0x0042D104` | 18 | data | labeled "retained state providers" (plural) in the work item; word shape is irregular, consistent with a small struct or short pointer list, not yet resolved |
| `0x0042D5C2..0x0042D84C` | 650 | code | real Thumb function bodies (`push {r2,r3,r4,lr}` family, `bl` calls) followed by another `0x0043xxxx`/`0x0022xxxx`-shaped literal/pointer run in the same recurring format seen at `0x0042E104` |
| `0x0042DAD0..0x0042DAE8` | 24 | data | six words that decode to ASCII `w`/`a`/`r` fragments interleaved with `0x2B`/`0x00`; no confirmed meaning |
| `0x0042E104..0x0042E1C4` | 192 | data (pointer table) | 48×4B words; 44 resolve to addresses inside the BL-012 span `0x00433000..0x00434477`, one (`0x0042DD15`) resolves to an already-landed function in this component, three are RAM addresses (`0x2001xxxx`/`0x2002xxxx`) or non-address constants |
| `0x0042E220..0x0042E224` | 4 | data | single word `0x0042FB00`, an in-range bootloader address (unresolved target) |
| `0x0042E458..0x0042E4A0` | 72 | data | same recurring `0x0043xxxx`-pointer/`0x0022xxxx`-pointer shape as `0x0042E104` and the `0x0042D5C2` tail |
| `0x0042E50E..0x0042E514` | 6 | data | 2B zero pad + word `0x08000140` (flash-range address shape) |
| `0x0042E534..0x0042E53C` | 8 | data | two words, `0x40000008` / `0x40000004` (peripheral-register address shape) |
| `0x0042E642..0x0042E644` | 2 | alignment | `00 00`, sits between two already-landed Thumb functions |
| `0x0042E6F2..0x0042E8A4` | 434 | code | real function (`push.w`, multiple `bl`); calls `0x0041B3E4`/`0x0041B3FC`/`0x004166AA`/`0x004176CE`, all in the BL-005 span, plus a trailing `0x0043xxxx`-pointer run |
| `0x0042E8C2..0x0042E8D0` | 14 | data | words `0x31200000`/`0x40080043`/`0x40244001`-shaped; mixed peripheral-address and unclear fields |
| `0x0042EDF6..0x0042EE00` | 10 | data | irregular; contains the same `0xC2F6E979` pattern seen inside `0x004301F4`'s literal cell below |
| `0x0042EE6C..0x0042EE70` | 4 | data | single word `0xC3889333`, no identified meaning |
| `0x0042F014..0x0042F020` | 12 | data | three words, `0xC47A0000`/`0x45800000`/`0x4494C000`-shaped (float-looking bit patterns) |
| `0x0042F14E..0x0042F1C8` | 122 | mostly data | leading bytes decode as a short helper fragment, remainder is a repeated `0x8xxx4003`-shaped table (30 words), consistent with a register-offset or pad-config list |
| `0x0042F3DA..0x0042FF00` | 2,854 | code + tables | ~600B of real Thumb code, then a ~200-entry 12-byte sparse `(index, small value, zero)` record table (index range `0x00..0xC8`, gaps present — NVIC-IRQ-count shaped), then a further block whose byte distribution does not resemble either code or the index table |
| `0x0042FFFE..0x00430000` | 2 | alignment | `00 00`, sits before the already-landed platform bring-up function |
| `0x004301F4..0x00430240` | 76 | data | contains repeated in-range bootloader addresses (`0x00434170`, `0x00431EA4`, `0x0043...`) and the same `0xC2F6E979` word seen at `0x0042EDF6` |
| `0x004303DE..0x00430470` | 146 | code | three near-identical 42-byte wrapper functions, each reading a signed 16-bit field at offset 0/2/4 of one struct and calling `0x0041DF48`/`0x0041DFC6`/`0x0041E09A` (all BL-005 range), plus a ~20-byte pointer tail |

## Recommended sequencing

Re-run BL-009 (or split it) after BL-005 and BL-012 land, since five of the
seven code spans and the one pointer-table span call or point directly into
those two ranges. The two pure zero-byte alignment spans
(`0x0042E642..0x0042E644`, `0x0042FFFE..0x00430000`) are independent of that
blocker and are the only immediately actionable bytes in this item, but at 4
of 5,978 bytes they were not worth a standalone overlay/manifest edit and
integration-lock cycle in isolation; fold them into whichever future pass
closes an adjacent span instead.

The `apollo_main` precedent for scattered literal/data spans is
`compile_in_place_data_group` (`g2/tools/apollo_overlay.py`), used by
`components/apollo_main/core_overlay/overlay.json`'s `in_place_data` list
for the Cordio SMP SC dispatch table — one `.rodata.<symbol>` C object,
verified by compilation, sliced into named `placements` at each stock
address. `apollo_bootloader/core_overlay/overlay.json` has no
`in_place_data` list yet; a genuine data close of the remaining unclaimed
cells here (once ownership is established, not merely byte-matched) should
use that same mechanism rather than `in_place_leaf`, which requires an
`STT_FUNC` Thumb symbol and is code-only.
