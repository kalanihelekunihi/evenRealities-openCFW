# GX8002 UART boot stage-1 rail-sequencing leaf (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 1,226 source-owned bytes
(vectors/table/traps 264, reset 48, divmod/stub 128, PMU trim bits 72,
polled UART 124, ID/bitmod 42, XIP 256, PMU fill 180, mdelay 112). This
tranche closes one further leaf as production-routed reviewed source in
the experimental codec candidate: **266 stock bytes replaced by 260
compiled bytes plus 6 generated fill bytes**. CD-001 is now
**1,492/8,192 bytes source-owned**.

## Envelope

| Symbol | Runtime | Package | Stock | Compiled | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_stage1_railc` | `0x10000B90` | `0xBE0` | 266 | 260 | compiled_c |

The envelope is the routine body `0x10000B90..0x10000C9A` only. The
callee `pmu_fill_desc` at `0x10000780` is the already-integrated pmufill
tranche; both the stock fill (stock side) and the recompiled source
fill (source side, linked at its entry in the same ELF) execute for
real in the battery — no modeled dependency.

## Behavior (decoded)

Fill `(id, desc)` into a 24-byte stack buffer; on nonzero return the
pass ends at the pop-and-check spinner. Otherwise `entry = desc[0]`,
`w3 = entry[3]`; null `w3` or null low byte exits too (those exits
observe fill exit-register leftovers and carry no outcome claim, see
below). Else `sel = desc[1] + b0`, `v = *sel`; when `arg1` equals the
low 25 bits the arm skips the body. The body: signed entry bytes
`b4 = entry[4]`, `b6 = entry[6]`; `cond = (arg2 == 0)` (stock `mvcv`
moves the inverted `cmpnei` condition, proven by the stored words);
the `desc[3]` bit arms `desc[5]`; the `desc[2]` cell bit selects one of
two seven-store sequences (`0x04000000, 0, 0x04000000`, then merged
`(cond<<27)|arg1` / `|0x06000000` variants) with an `mcell` clear before
and a merge-back after on the set path; a set `desc[3]` bit latches
`desc[4]`. The status cell is re-read before clearing (fresh status,
not the bit-test snapshot). Every path ends in the pop-and-check
spinner; there is no `rts`.

Three decoded facts route this tranche:

1. The spin check observes the **caller r5**, not arg2: the entry
   `mov r5, r2` is clobbered by the pop, which restores the pushed
   caller value. Caller r5 is therefore an explicit battery input.
2. The skip arm jumps to the check **without popping**, so its first
   check observes the live arg2. Only post-pop checks see caller r5.
3. On desc[4]-store paths the `ld.w r2, (sp, 16)` reload repoints the
   checked word at the desc[4] **address** itself, so the check observes
   a per-domain-constant address bit. Past the first check r2 has
   decayed to 0/1, so later checks always expect 1: body re-polls pop in
   {1, 2}, skip pops in {0, 1, 2}. The re-poll edge itself (branch back
   into the body, re-reading the caller frame as descriptor words)
   needs the 0xDDC orchestrator frame and stays a followup; the C keeps
   popping instead.

## Provenance

Clean-room MIT C in
`components/shared/gx8002/runtime_gx8002_uart_stage1_railc.c`. No SDK
text is reproduced and no SDK register map is used: every address comes
from the fill-provided descriptor and every constant is a stock
immediate. See
`NATIONALCHIP-UART-BOOT-STAGE1-RAILC-NOTICE.txt`. Two compiler-order
findings are pinned in code: a `memory` barrier keeps the status read
after the arm (GCC otherwise hoists it above the desc[3]/desc[5]
traffic), and the entry byte is sampled once into a local (a second
volatile read would emit a duplicate MMIO access the battery rejects).

## Verification

`g2/tools/verify_gx8002_uart_stage1_railc.py` (report
`docs/research/gx8002-uart-stage1-railc-verification.json`,
**672 cases**, zero exclusions):

- Compiles the C with `-Os -mcpu=ck804ef -mhard-float -ffreestanding
  -fno-builtin -ffunction-sections -fdata-sections
  -fno-tree-loop-optimize -fno-jump-tables` (with `-Wall -Wextra
  -Werror` from the shared flags), links the section at its runtime
  entry together with the recompiled fill into one `railc.elf` with no
  undefined symbols and no relocations; the 260-byte section fits the
  266-byte envelope at aligned package offset `0xBE0`.
- The stock span is rewrapped with the CK804EF ELF flags and shifted to
  its runtime base (the `gx8002-uart-boot-stage1-cd001-analysis.md`
  recipe) so decoded addresses are absolute on both sides.
- Decoded-target execution of stock vs linked body over a flat word-RAM
  model (peripheral table, entry/b0 cells, both domain MMIO cells,
  stack window plus caller frame; unmapped addresses trap): identical
  **unfiltered** access traces (kind, address, width, value of every
  read/write, including push/pop traffic — both frames are exactly 24
  bytes, so no window is excluded), identical descriptor values via the
  captured fill-call argument, identical final RAM, identical popped
  registers. Each case runs stock through its re-poll decision and the
  source through the same pops (0–2).
- Independent Python oracle on every case: fill gate/match/domain
  order, entry gating, selector poll, both store tails, push/pop
  modeling, and the stateful check sequence, stated from the decoded
  structure rather than the decoded instructions. The oracle agrees
  with stock on all 672 traces, descriptors, RAM states, and pop
  counts.
- Battery: 3 table modes (direct, entry-0 fallback, scan hit) x ids
  {2, 9, 10, 20} (PMU and MCU domains) x b0 {4, 0x10} x entry bytes
  (b4 in {0, 3, 31, -5, -128}, b6 in {0, 1, 7, 30, -3}) x d3/m bit
  set/clear x arg1 (bit27 set/clear, skip-matching) x arg2 {0, 1} x
  caller r5 {0, 1}: 336 bases x 2 = 672 admitted (pops {0: 96, 1: 288,
  2: 288}).
- `g2/tests/test_gx8002_uart_stage1_railc.py` (21 tests): interpreter
  unit checks for the exercised opcodes (`mvcv` inversion, signed
  `blz`, `ld.b`/`ld.bs`, `sextb`/`zextb`, masked register shifts,
  `nor`/`xor`/`andi`, push/pop, `bsr`/`rts`, rejections), oracle path
  and pop-count checks, full-battery predict/oracle agreement,
  structural edge coverage, stock-envelope regression, and
  fit/no-relocation regression. Native host execution is infeasible
  (the leaf dereferences 32-bit target addresses that truncate on the
  64-bit host); the interpreter tests execute the compiled target
  object instead.

Accepted boundary (documented, not verified): fill-fail and null-entry
exits observe fill exit-register leftovers (implementation-defined);
the C keeps the same branches without an outcome claim there. Register
shifts by a register count use the low 5 bits (both sides share the
executor, so agreement holds by construction; hardware semantics for
negative counts unqualified). The re-poll body re-entry needs the
0xDDC orchestrator frame. Hardware timing and whole-device behavior
remain unqualified (`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-railc` in
`tools/build_gx8002_source_candidate.py` (artifact `railc.elf`,
baseline above) and in the `gx8002-source-candidate` test list in
`g2/Makefile`. The shared `make -C g2 gx8002-source-candidate` gate was
not run here: it currently fails before reaching any stage-1 tranche at
a pre-existing stale baseline owned elsewhere (same `rtc-init` pin drift
reported by the prior tranches; left for its owner). Tranche admission
was verified through the builder's exact `reviewed_replacements` +
`compose` path in a private output dir: 1 replacement, 260 compiled
bytes + 6 generated fill, ownership split at package `0xBE0..0xC9A`,
firmware size unchanged. The generated
`gx8002-source-candidate-build.{json,md}` and experimental manifest
pins regenerate from the green shared run, so they are deliberately not
hand-edited here.

## Remains (CD-001, still retained)

CD-001 is now 1,492/8,192 bytes source-owned (1,226 prior + 266 here).
Still retained: init routine (`0x100001BC`), handshake orchestration
(`0x100001FC`), receive loop (`0x100002C8`), time-ms leaf (`0x100003BC`,
dead-path trap, envelope too small), the `0x1000046C`/`0x100004A4`
trap tails, the beacon (`0x100004D0`), configure/announce/handshake
(`0x100005C4`/`0x1000065C`/`0x100006D8`), rail ops A/B
(`0x10000860`/`0x10000A30`, same pop-spinner family as this tranche),
the `0x10000C9C` flow, both dispatchers (`0x10000D98`/`0x10000EA0`,
D98 fit floor 298 B vs 264 B envelope, deferred) and everything they
gate, the rail sweep (`0x10001378`), the `0x100019C0` region,
postambles, the `0x10001DDC` orchestrator, and the `0x10001E60..0x10002000`
tables (compiler layout for the retained dispatchers, must stay
retained). Hardware qualification stays blocked by unavailable physical
evidence.
