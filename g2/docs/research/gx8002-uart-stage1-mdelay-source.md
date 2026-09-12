# GX8002 UART boot stage-1 millisecond-delay leaf (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 1,114 source-owned bytes
(vectors/table/traps 264, reset 48, divmod/stub 128, PMU trim bits 72,
polled UART 124, ID/bitmod 42, XIP 256, PMU fill 180) and mapped the
remainder (`gx8002-uart-stage1-tickdiv-source.md`). This tranche closes
one further leaf as production-routed reviewed source in the
experimental codec candidate: **112 stock bytes replaced by 92 compiled
bytes plus 20 generated fill bytes**. CD-001 is now 1,226/8,192 bytes
source-owned.

## Envelope

| Symbol | Runtime | Package | Stock | Compiled | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_stage1_mdelay` | `0x100003FC` | `0x44C` | 112 | 92 | compiled_c |

The envelope is the routine body `0x100003FC..0x1000046C` only. Both
terminal paths pop the saved registers and chain into the retained
rail-configure flow at `0x1000046C`; there is no return.

## Behavior (SDK-identified)

The leaf is an inlined `spl_mdelay`/`spl_udelay(1000)` pair from the
pinned NationalChip grus SDK `arch/soc/grus/spl/spl_counter.c`
(commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`):

- Outer loop: exact `while (msec--)` post-decrement shape, including the
  zero-count early exit with the argument register already wrapped to
  `0xFFFFFFFF`.
- Per millisecond: one 64-bit counter-2 snapshot (VALUE `+0x04` then
  ACCSNAP `+0x08` under `GX_REG_BASE_COUNTER = 0xA0400000`, matching
  `gx_get_time_us`), plus 1000, polled with strict less-than
  (`while (now < tmp + 1)`, constant-folded to a +1001 deadline with a
  greater-or-equal exit, matching the stock `add.64`/cascade).
- Snapshot/poll read counts match stock exactly (one LO/HI pair per
  snapshot on both sides).

Only the counter addresses, the 1 MHz rate fact, and the +1000/+1 loop
shape cross the boundary; the C body is clean-room. No SDK text is
reproduced. See `NATIONALCHIP-UART-BOOT-STAGE1-MDELAY-NOTICE.txt`.

## Verification

`g2/tools/verify_gx8002_uart_stage1_mdelay.py` (report
`docs/research/gx8002-uart-stage1-mdelay-verification.json`, 160 cases):

- Compiles the C with `-Os -mcpu=ck804ef -mhard-float -ffreestanding
  -fno-builtin -ffunction-sections -fdata-sections -fno-tree-loop-optimize
  -fno-jump-tables`, links the section at its runtime entry into one
  `mdelay.elf` with no undefined symbols and no relocations; the 92-byte
  section fits the 112-byte envelope at aligned package offset `0x44C`.
  The retained `0x1000046C` entry is a linker-assigned absolute symbol
  (reset-entry precedent), not a relocation.
- Shape gate (fail-closed): the section must open with exactly
  `push r4-r5, r15`, contain exactly one `pop r4-r5, r15` (the
  source-level restore balancing it), exactly one `bsr` to `0x1000046C`,
  no stack-pointer frame, no intra-section-external branches, and no
  `rts`/`bkpt`/`jmp`. A toolchain change that moves the save alters the
  balance and is rejected instead of silently unbalancing the stack.
- Decoded-target execution of stock vs linked body over a counter-2
  RAM model (VALUE/ACCSNAP cells advancing a deterministic 577 ticks
  per snapshot) plus a stack window: identical exact access traces
  outside the window, identical `r0` (`0xFFFFFFFF` on every path),
  identical callee-saved registers and stack pointer, identical final
  counter cells.
- Independent Python oracle on every case: post-decrement millisecond
  count, snapshot-plus-1000 deadlines, strict-less-than polls, stated
  from the decoded structure rather than the decoded instructions.
- Battery: counts {0,1,2,3,4,5,6,7,8,9,10,16,17,32,64,255} x LO
  {0, 1, 0xFFFFF000, 0x12345678, 0xFFFFFFFF} x HI {0, 0xFFFFFFFF}:
  zero-count skip, small counts, 64-bit carries, deadline wrap, and a
  long 255-count run per seed.
- `g2/tests/test_gx8002_uart_stage1_mdelay.py` (13 tests): host
  execution of the C leaf against a redirected counter (zero-count
  exact case; advancing-counter thread case with hang guard),
  interpreter unit checks for the newly exercised opcodes (`add.64`,
  multi-register `push`/`pop`, chaining-stop preservation),
  stock-envelope regression, and fit/no-relocation regression.
- New interpreter semantics follow established repo conventions
  (`add.64` as low-plus-high-with-carry over the adjacent register
  pair); each is pinned by stock/source/oracle agreement on every
  battery case, not just by convention.

Accepted boundary (documented, not verified): the counter is modeled
RAM advancing per snapshot, not hardware time; counts above 255 use the
same code paths but are not in the battery; stack-window slot
assignment is excluded as compiler scratch while counter cells are
compared exactly; the chaining `bsr` clobbers the link register, which
is dead (the `0x46C` flow saves it on entry and never returns) and is
compared only up to the chaining instruction. Hardware timing and
whole-device behavior remain unqualified (`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-mdelay` in
`tools/build_gx8002_source_candidate.py` (artifact `mdelay.elf`,
baseline above) and in the `gx8002-source-candidate` test list in
`g2/Makefile`.

## Remains (CD-001, still retained)

CD-001 is now 1,226/8,192 bytes source-owned (1,114 prior + 112 here).
The `0x1000046C` handoff target stays retained (rail-configure flow,
blocked on the `0x10000D98`/`0x10000EA0` dispatchers); the dispatcher
tranche itself is analyzed and deferred (see the D98 appendix to
`gx8002-uart-stage1-tickdiv-source.md`: 292 compiled bytes vs the
264-byte envelope, with the branch-vs-table density gap itemized).
Still retained: init routine, chip-id/early-UART routine, receive
routine, the `0x10000C9C` flow, both dispatchers and everything they
gate, the rail sweeps, the orchestrator, and the table region.
Hardware qualification stays blocked by unavailable physical evidence.
