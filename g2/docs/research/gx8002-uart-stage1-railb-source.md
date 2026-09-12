# GX8002 UART boot stage-1 rail-sequencing operation B (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 1,492 source-owned bytes
(vectors/table/traps 264, reset 48, divmod/stub 128, PMU trim bits 72,
polled UART 124, ID/bitmod 42, XIP 256, PMU fill 180, mdelay 112,
rail C 266). This tranche closes one further leaf as
production-routed reviewed source in the experimental codec candidate:
**350 stock bytes replaced by 350 assembled bytes, zero fill**. CD-001
is now **1,842/8,192 bytes source-owned**.

## Envelope

| Symbol | Runtime | Package | Stock | Compiled | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_stage1_railb` | `0x10000A30` | `0xA80` | 350 | 350 | compiled_assembly |

The envelope is the routine body `0x10000A30..0x10000B8E` only. The
callee `pmu_fill_desc` at `0x10000780` is the already-integrated pmufill
tranche; both the stock fill (stock side) and the recompiled source
fill (source side, linked at its entry in the same ELF) execute for
real in the battery — no modeled dependency. The two zero bytes at
package `0xBDE..0xBE0` are alignment padding before rail C and stay
retained.

## Behavior (decoded)

Fill `(id, desc)` into a 24-byte stack buffer; on nonzero return the
pass ends at the pop-and-update loop. Otherwise `entry = desc[0]`,
`w3 = entry[2]`; null `w3` or null low byte exits too (those exits
observe fill exit-register leftovers and carry no outcome claim, see
below). Else `r18 = w3[1]`, `r13 = w3[2..3]`, `sel = desc[1] + b0`,
`v = *sel`; when `arg1[15:0]` equals the gated word (`(v >>
r18) & r13`, plus one when nonzero) the skip arm jumps to the loop
with implementation-defined registers (no outcome claim). Otherwise
the body: a bit-length poll over `r13` (zero mask takes the shortcut),
signed entry bytes `b4 = entry[4]`, `b6 = entry[6]`; the `desc[3]`
bit arms `desc[5]`; when the `desc[2]` cell bit is set, the id gate
(`id == 6 || id >= 10`, decoded from the `cmpnei/cmphs/bf` pair —
an earlier draft used `>= 9` and the battery rejected it) selects the
rotl fold tail; the selector word goes through a clear/set/merge
sequence; a set cell bit with a gated id folds the cell once more
before the first check. The first check latches `desc[4]` when the
arm bit is set. Every path ends in the pop-and-update loop, which
frees the frame, restores the saved registers, folds one status bit
into the `desc[2]` cell, re-checks, latches, and repeats forever;
there is no `rts`.

Two decoded facts route this tranche:

1. The shift/mask (`r18`/`r13`) come from the descriptor's own byte
   cell (`w3+1`/`w3+2`), not from the table entry — an early draft
   read entry bytes 1..2 and the battery rejected it, since the fill
   only constrains entry word 0. The poll loop, nonzero shifts, and
   the merge-skip arm are all genuinely reachable and all covered.
2. The loop never observes the popped caller registers (no branch
   reads them after a pop), so the caller frame only needs to be
   mapped: every caller word holds a scratch address, which also
   keeps the per-pass latch stores mapped. `arg2` is dead on every
   path (overwritten before any use) and is swept to prove it.

## Provenance

Clean-room assembly in
`components/shared/gx8002/runtime_gx8002_uart_stage1_railb.S`. A
clean-room C draft was attempted first and abandoned: a 22-variant
flag probe (`-Os`/`-Oz`/`-O1`/`-O2` plus single `-fno-*` options)
floors at 470–474 bytes against the 350-byte envelope (plain `-Os`
474, `-Oz` 474, `-O2` 470; `-fno-tree-loop-optimize` hurts here), so
no C shape fits without dropping general-form code. The draft was
removed from the tree; the measurement is recorded here so followups
do not repeat it. The admitted assembly keeps the stock register plan
and control flow (it links byte-identically, which corroborates the
transcription but is not the admission claim). No SDK text is
reproduced and no SDK register map is used: every address comes from
the fill-provided descriptor and every constant is a stock immediate.
See `NATIONALCHIP-UART-BOOT-STAGE1-RAILB-NOTICE.txt`.

## Verification

`g2/tools/verify_gx8002_uart_stage1_railb.py` (report
`docs/research/gx8002-uart-stage1-railb-verification.json`,
**7,680 cases**, zero exclusions):

- Assembles the `.S` with the tranche flags, links the section at its
  runtime entry together with the recompiled fill into one `railb.elf`
  with no undefined symbols and no relocations; the 350-byte section
  exactly fills the 350-byte envelope at aligned package offset
  `0xA80`.
- The stock span is rewrapped with the CK804EF ELF flags and shifted
  to its runtime base (the `gx8002-uart-boot-stage1-cd001-analysis.md`
  recipe) so decoded addresses are absolute on both sides.
- Decoded-target execution of stock vs linked body over a flat word-RAM
  model (peripheral table, entry/b0 cells, domain MMIO cells, stack
  window plus scratch-valued caller frame; unmapped addresses trap):
  identical **unfiltered** access traces (kind, address, width, value
  of every read and write, including push/pop traffic — both frames
  are exactly 24 bytes, so no window is excluded), identical
  descriptor values via the captured fill-call argument, identical
  final RAM, identical registers (all 32 plus sp) at the stop point.
  Each case runs the body plus exactly four loop passes.
- Independent Python oracle on every case: fill gate/match/domain
  order, entry gating, selector poll, bit-length poll, arm, id-gated
  rotl tail, selector store sequence, first fold/check/latch, and four
  modeled loop passes, stated from the decoded structure rather than
  the decoded instructions. The oracle agrees with stock on all 7,680
  traces, descriptors, RAM states, and loop-carried registers.
- Battery: 3 table modes (direct, entry-0 fallback, scan hit) x ids
  {2, 6, 9, 20} (PMU/MCU domains, id-gate armed/unamed) x b0 {4, 0x10}
  x (shift,mask) {(0,0), (1,1), (7,0x1f), (3,0xffff), (29,0x8001)} x
  entry bytes (b4 in {0, 3, 31, -5, -128}, b6 in {0, 1, 7, 30, -3}) x
  d3/m bit set/clear x sel_init {0, 0xffffffff} x arg1 (two low-16
  values avoiding the skip gate, including the merge-skip low16 == 0
  on nonzero-gate shapes: 1,536 cases) x arg2 {0, 1}.
- `g2/tests/test_gx8002_uart_stage1_railb.py` (23 tests): interpreter
  unit checks for the exercised opcodes (`ld.h` zero-extend and span
  rejection, `zexth`, `rotl` two/three-operand and count wrap,
  `andn`, masked register shifts, `blz`, byte loads, `inct`, push/pop,
  `bsr`/`rts`, rejections), oracle gate math (skip gate, id-gate arm
  pinned by cell access count), arg2-dead check, leftover-path
  no-prediction checks, full-battery edge coverage, stock-envelope
  regression, and fit/no-relocation/byte-identity regression. Native
  host execution is infeasible (the leaf dereferences 32-bit target
  addresses that truncate on the 64-bit host); the interpreter tests
  execute the assembled target object instead.

Accepted boundary (documented, not verified): fill-fail, null-entry,
and selector-match exits observe fill exit-register leftovers
(implementation-defined); the assembly keeps the same branches
without an outcome claim there. Register shifts by a register count
use the low 5 bits (both sides share the executor, so agreement holds
by construction; hardware semantics for negative counts
unqualified). `ld.h` is modeled zero-extending, and bit-15-set masks
(`0xffff`, `0x8001`) are covered by the battery with full
stock/oracle agreement, so the zero-extending reading is pinned
against stock to the extent of these cases; silicon-level load
semantics beyond the decoded model stay unqualified, as does
hardware timing and whole-device behavior
(`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-railb` in
`tools/build_gx8002_source_candidate.py` (artifact `railb.elf`,
baseline above) and in the `gx8002-source-candidate` test list in
`g2/Makefile`. The shared `make -C g2 gx8002-source-candidate` gate
was not run here: it currently fails before reaching any stage-1
tranche at a pre-existing stale baseline owned elsewhere (same
`rtc-init` pin drift reported by the prior tranches; left for its
owner). Tranche admission was verified through the builder's exact
`reviewed_replacements` + `compose` path in a private output dir
(`g2/build/continue-analysis/CD-001/railb-compose`): 1 replacement,
350 compiled bytes, ownership split at package `0xA80..0xBDE`,
firmware size unchanged. The generated
`gx8002-source-candidate-build.{json,md}` and experimental manifest
pins regenerate from the green shared run, so they are deliberately
not hand-edited here.

## Remains (CD-001, still retained)

CD-001 is now 1,842/8,192 bytes source-owned (1,492 prior + 350
here). Still retained: init routine (`0x100001BC`), handshake
orchestration (`0x100001FC`), receive loop (`0x100002C8`), time-ms
leaf (`0x100003BC`, dead-path trap, envelope too small), the
`0x1000046C`/`0x100004A4` trap tails, the beacon (`0x100004D0`),
configure/announce/handshake (`0x100005C4`/`0x1000065C`/`0x100006D8`),
rail op A (`0x10000860`, ~464 B, same pop-update family as this
tranche — expect the same C-fit outcome and the same assembly route),
the `0x10000C9C` flow, both dispatchers (`0x10000D98`/`0x10000EA0`,
D98 fit floor 298 B vs 264 B envelope, deferred) and everything they
gate, the rail sweep (`0x10001378`, ~600 B two-exit loop, mapped this
pass: not a small target), the `0x100019C0` region, postambles, the
`0x10001DDC` orchestrator, and the `0x10001E60..0x10002000` tables
(compiler layout for the retained dispatchers, must stay retained).
Hardware qualification stays blocked by unavailable physical
evidence.
