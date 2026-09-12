# GX8002 UART boot stage-1 rail postamble source (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 2,570 source-owned
bytes. This pass closes the **rail postamble at runtime `0x10001D9C`
(package `0x1DEC`, 60 bytes: 56 of code plus the 4-byte literal pool
word)** as reviewed clean-room assembly, verified by 2,268 decoded
stock/source/oracle cases plus 14 host tests, and registered as
`uart-stage1-postamble` in the experimental codec builder. **CD-001 is
now 2,630/8,192 bytes source-owned; 5,562 bytes remain.**

## 1. What the leaf is

The small flow at the end of the rail-programming region
(`0x10001D9C..0x10001DD8`, package `0x1DEC..0x1E28`):

```
push r15
lrw r3, 0x20002274            ; base pointer cell
r2 = [r3]
[r2+0x3A0] |= 0x101           ; set control bits 0 and 8
poll: r3 = [r2+0x2C0]; while ((r3 & 1) == 0) poll
r3 = [r2+0x3A0] & ~0x101      ; clear the control bits
[r2+0x3A0] = r3; r1 = 0
[r2+0x398] = 0                ; publish id 25, selector 0
r0 = 25; bsr 0x10000D98       ; noreturn into the first dispatcher
pop r15                        ; never executed (dispatcher noreturn)
pool: .word 0x20002274
```

The leaf takes no register inputs: `r0`/`r1` are set explicitly
before any use (`movi` overwrites dominate), and `r6` passes through
untouched into the dispatcher as its entry selector. The only RAM
inputs are the pointer cell, the three base cells, and the dispatcher
slice (fill tables, entry bytes, select cells, caller window). The
`rts` at `0x10001DD8` and the padding halfword after it stay retained
stock: they are unreachable in the model because the dispatcher never
returns (no `rts`/register-out jump in `0x10000D98..0x10001094`,
established this pass by full-range transfer inventory), so they are
never executed on either side.

## 2. Why assembly, and why byte-identical

A C shape was not attempted: the envelope holds a hand-written
push/`bsr`/pop skeleton with an inline literal pool and a 32-bit
`bez` poll branch that GCC `-Os` has no reason to reproduce densely,
and the pmudispatch precedent already establishes assembly as the
admitted form for this idiom. The transliteration needed no
peepholes: every encoding the assembler picks (16-bit push/pop,
`lrw`, all loads/stores, `ori`/`andi`, both `bclri`, both `movi`,
32-bit `bez`, 32-bit `bsr`) matches the stock bytes, and the
assembler's own end-of-section literal pool for the numeric `lrw`
lands exactly on the stock pool word (the numeric-`lrw` precedent of
the reviewed stage-1 reset entry). The verifier pins byte identity of
the linked 60-byte payload against the stock envelope on top of the
trace battery. A label-based pool was rejected during construction:
it takes the address-load indirection form (extra slot + relocation),
so the source uses the numeric constant with no explicit `.word`.

## 3. Composition decisions

- The real linked dispatcher and fill bodies run on both sides
  (stock pair for stock, compiled source pair for source), the same
  composition the pmudispatch verifier uses for fill.
- Execution starts with sp 4 bytes high (`SP0+4`), so the
  dispatcher's push+frame lands exactly on the standalone dispatcher
  layout the admitted battery maps; the extra push word is compared
  exactly like every other access. The battery RAM for the
  dispatcher-id-25 slice is the admitted `config_ram` output verbatim
  plus the pointer cell and three base cells.
- The dispatcher oracle is the admitted pmudispatch oracle restated
  for the composed entry (`disp_oracle_composed`): the single
  difference is the pushed return address, which is the postamble's
  call site (`0x10001DD2 = ENTRY+54`) rather than the standalone
  seed, because the leaf reaches the dispatcher through a real `bsr`.
  This was caught by the battery itself (first run diverged at the
  fourth push word: seed vs `0x10001DD2`), not by inspection.
- Id 25 passes both dispatcher table guards, so the retained jump
  tables are pinned by `check_tables` but not exercised by this
  battery; table-driven arms stay covered by the pmudispatch battery.
  A host test pins this passthrough explicitly.
- The single-pass poll shape is pinned; a clear poll bit spins both
  sides on the same three byte-identical instructions, so no
  multi-pass case is needed. Dispatcher fill failures observe fill
  scratch leftovers (see the pmudispatch audit) and stay out; id 25
  matches both fills in every battery case.

## 4. Verification

- 2,268 stock/source/oracle cases: full unfiltered access-trace,
  final-RAM, and live-register (`r0/r2/r3/r4/r5/r6/r14/r15`)
  agreement from entry through handoff into retained `0x10000EA0`.
  Entry r0/r1 garbage x2; caller r6 nonzero/zero; entry bytes
  -1/0/edges/sign-extended; select-cell bit pairs; 1-pass and 4-zero
  walks; control-word starts 0/`0x101`/`0xFFFFFFFF`; poll
  don't-care bits; two base addresses.
- 14 host tests: interpreter units (single push, poll gate + spin,
  control-bit ops, `bsr` admission/rejection, traps), prefix model
  (entry-reg independence, push/cell trace shape, poll exclusion,
  table passthrough, dump pins, battery scale), and placement
  (envelope hash, exact 60-byte fill, alignment, no relocations,
  byte identity).
- Jump-table contents are pinned against the stock dump and fail
  closed on drift.

## 5. What remains for CD-001 (5,562 bytes)

Unchanged critical path: the `0x10000EA0` second dispatcher is now
mapped (500-byte envelope `0xEA0..0x1094` incl. its `0x10001EF4`
20-entry table for ids 7..26, pool at `0x1080..0x1093`): every
branch target is internal, its only `bsr`s go to the reviewed fill,
and its table jumps land in the first dispatcher's shared arms
(`0xE28..0xE8C`), which re-enter the dispatcher complex — the two
dispatchers form one noreturn state machine (no `rts`/register-out
jump anywhere in `0xD98..0x1094`; any exit is via unqualified
IRQ/timing). Closing it needs a bounded-cycle or cut-point battery,
a larger tranche than this pass. The `0x10000C9C` UART-config
block, `0x1000046C`, handshake/init/beacon, the `0x10001094` flow
(blocked on `0x100019C0`), the `0x10001378` sweep, the orchestrator,
and the `0x10001E60..0x10002000` tables (retained compiler layout)
follow it. Hardware qualification stays blocked by unavailable
physical evidence.
