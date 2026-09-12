# G2 bootloader BL-006 SPOT trim-search span source closure

Date: 2026-09-12. Work item BL-006 (done: the last 1,316 bytes).

## Result

The final retained BL-006 region -- the 1,316-byte binary32/SPOT
span `0x00427E54..0x00428378` -- is now produced from reviewed
MIT C through the component's `in_place_leaves` mechanism. Four
dead interiors after entry-redirect-replaced heads, in one new
source file:

| Leaf | Range | Bytes | Calls |
| --- | --- | --- | --- |
| `..._spot_trim_classify_tail_427e54` (T0) | `0x00427E54..0x00427E84` | 48 | 0 |
| `..._spot_trim_search_a_427e84` (F1) | `0x00427E84..0x00428068` | 484 | 9 |
| `..._spot_trim_search_b_428068` (F2) | `0x00428068..0x00428240` | 472 | 8 |
| `..._spot_trim_search_c_428240` (F3) | `0x00428240..0x00428378` | 312 | 4 |

New source: `runtime_bl006_spot_trim_span_427e54.c` (MIT; each
leaf is a naked-assembly target body plus a portable C twin for
host testing). Every payload compiles under the reviewed
Apple-clang Cortex-M55 leaf flags and reproduces the
authenticated stock bytes exactly (`expected.sha256` equals
`stock.sha256`; full SHAs match the survey pins `609d289f...`,
`b5072ed7...`, `7828372b...`, `aed159d1...`). All 21 calls
resolve as reviewed `R_ARM_THM_CALL` relocations to
source-named symbols (trim finalize, retained delay, IRQ
pause/resume, SPOT timer service, ton-adjust, transition
start).

BL-006 stands at 5,892 of 5,892 bytes from reviewed source
(77/77 regions). The verifier is
`g2/tests/test_runtime_bootloader_bl006_spot_trim.py` (14
tests).

## Semantics (from anchored Capstone decode)

- T0 is the suffix tail of the stock float classifier: the
  entry FPSCR N flag (head-owned) set returns 2, else s0 is
  compared against the in-span pool words `50.0f`
  (`0x00428060`) and `1000.0f` (`0x00428064`): below 50.0
  returns 4, in `[50.0, 1000.0)` returns 3, at/above 1000.0
  returns 4. A NaN operand leaves VCMP flags N=Z=C=V=1, so
  neither `blt` nor `bpl` is taken and the tail falls through
  to 3; the twin encodes exactly that.
- F1/F2/F3 are three trim-search/measure variants over the
  trim table at `0x20026BA0`: gate on bit0 of `0x400083E0`,
  an up-to-60 delay-poll loop on bit30 of `0x40008064`, the
  timer service, SRAM publishes, ton-adjust, saturating trim
  clamps, conditional IRQ pause/resume on bit17 of
  `0xE000ED14`, and power/field publishes. F1 alone keeps the
  trim-match path (finalize plus status byte `0x1A`); F2 has
  two clamps (into `0x4002004C` and `0x40020044`); F3 has no
  IRQ pause/resume, merges the word at table `+0x50` into
  `0x4002004C`, stores the trim id, then calls
  `transition_start` with `r0 = 50` (there is no `delay(50)`
  in F3) and writes status byte `0x02`.
- The four scratch-byte selects from the table word at
  `+0x64` are dead in all three variants (both loaded bytes
  are overwritten before any use); the twins omit them.
  F2/F3 reload `r0` from `sl` before ton-adjust, so
  ton-adjust always receives `(sl, r4)`; the twins record
  that directly.

## Reviewed encodings

No `.inst`/`.inst.w` spellings were needed: every
`ldr.w [pc, #imm]` reuses a retained SPOT-table slot through
its stock immediate, which encodes identically in the
relocatable object (bitmap-client precedent), and every call
names a source-owned symbol. The VFP mnemonics (`vldr`,
`vcmp.f32`, `vmrs`) assemble natively under the reviewed
flags (reference-assembler probe). F1's 14-byte tail after
its return (2-byte pad, head-owned word `0xC3888000`
retained verbatim, `50.0f`, `1000.0f`) is reproduced with
`.word` spellings. There are no probes; the byte-exact
rebuild plus the relocation-set check pins every immediate.

## Twin verification (unicorn execution differential)

The F1/F2/F3 twins were checked against real execution of
the stock Thumb bodies under unicorn: 180 randomized trials
(60 per leaf) comparing the full 15-cell memory image plus
the complete call trace (callee, arguments, order). The
differential caught and fixed two real twin bugs before
landing: the clamp gate `cmp d, #1; blt` is a *signed*
compare (q is 0 unless d >= 1), and F2's post-`delay(5)`
`s
...[truncated 3073 chars]
