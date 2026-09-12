# GX8002 UART boot stage-1 first PMU dispatcher source (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 2,306 source-owned
bytes. This pass closes the **`0x10000D98` dispatcher envelope
(package `0xDE8`, 264 bytes)** as reviewed clean-room assembly,
verified by 8,370 decoded stock/source/oracle cases plus 13 host
tests, and registered in the experimental codec builder.
**CD-001 is now 2,570/8,192 bytes source-owned; 5,622 bytes remain.**

## 1. What was closed

- Source: `components/shared/gx8002/
  runtime_gx8002_uart_stage1_pmudispatch.S` (reviewed assembly,
  assembles to exactly 264 bytes, zero relocations after linking).
- Notice: `components/shared/gx8002/
  NATIONALCHIP-UART-BOOT-STAGE1-PMUDISP-NOTICE.txt` (clean-room
  statement, abandoned-C-draft record, MIT).
- Verifier: `g2/tools/verify_gx8002_uart_stage1_pmudisp.py`
  (`verify()` entry consumed by `build_gx8002_source_candidate.py`).
- Test: `g2/tests/test_gx8002_uart_stage1_pmudisp.py` (13 tests).
- Report: `g2/docs/research/gx8002-uart-stage1-pmudisp-verification.json`.
- Registration: `uart-stage1-pmudisp` in
  `g2/tools/build_gx8002_source_candidate.py` plus the
  `gx8002-source-candidate` test list in `g2/Makefile`.
- Removed: the deferred 298-byte C draft
  (`runtime_gx8002_uart_stage1_pmudispatch.c`, unregistered) is
  superseded by this tranche; its fit measurements (312 B plain
  tranche flags, 298 B floor with `-fno-jump-tables
  -fno-guess-branch-probability -fno-cse-follow-jumps -fno-gcse`,
  368/352 B at -O1/-O2) are preserved here so followups do not
  repeat them.

## 2. Decoded behavior (from stock bytes, analysis oracle only)

Entry `(id, sel)`: `push r4-r6, r15; subi sp, 24` (24-byte
descriptor at the frame base). `sub = id-7`; if `sub >= 18` the id
passes through, else the retained jump table at `0x10001E60` (18
entries, ids 7..24) selects the fill id (7,8->2; 17,18->16;
20,21->19; 23,24->22; all others passthrough). First
`pmu_fill_desc` call; on failure skip to the second fill. On
success, entry byte 6 (signed) gates: `-1` skips to the second
fill; otherwise fills `< 10` with `(fill<<1) & 579 != 0` take the
extended test, all others the alternate test (details below).
`store4` writes `(1u << entry[4])` to the fourth descriptor word;
the fifth-word store applies on the nonzero-selector path. Second
`pmu_fill_desc` call with the original id; on failure take the tail
walk. Otherwise `(1u << entry[5])`, folded with the status bit from
the retained jump table at `0x10001EA8` (19 entries, ids 6..24:
6,14->`0x8000`; 11->8; 13->`0x2000`; 17->`1<<16`; 18->`1<<17`;
20->`1<<18`; 21->`1<<19`; 23->`1<<20`; 24->`1<<21`; every other id
runs the check arm, which clears id bit 2 and fails on id 1 or a
zero bit). Selector nonzero stores to the fifth word and hands off;
selector zero stores to the fourth word and walks. Every terminal
path pops the frame and falls into the retained second dispatcher
at `0x10000EA0` (no `rts`). The zero-selector tail pops the frame
and re-enters the bit arms with caller registers, consuming 40
caller-stack bytes per pass until a nonzero selector word is
observed; the caller r6 is therefore an explicit battery input.

## 3. Two stock-ground-truth corrections to prior readings

These were proven by stock-side program-counter traces during this
pass (not by re-reading the disassembly); the prior appendix text
that disagrees is superseded here:

1. **Three-operand shifts execute reversed.** Printed
   `(rd, rx, ry)` computes `ry OP rx`. Proof A (mask):
   `tlsl r5, r3, r5` with `r3=1, r5=fill` sends fill 0 to the
   alternate arm and fill 9 to the extended arm, i.e. it tests
   `(fill<<1) & 579`, not `(1<<fill) & 579`. Proof B (extended):
   `tlsr r0, r3, r0` with `r0 = b6+1 = 1`, cell `0xA5A5A502`
   falls through to the plain shift, i.e. it computes
   `(1 >> (cell & 31)) & 1 = 0`, not `(cell >> 1) & 1 = 1`. Both
   sites agree; no site contradicts. Two-operand shifts are
   standard (`rd OP rs`). The earlier appendix claim
   ("`tlsl r5,r3,r5` = `1<<fill` idiom") is corrected: the mask
   test is `(fill<<1) & 579` and the extended test is
   `((b6+1) >> (cell & 31)) & 1`. The executor, oracle, and battery
   all use the corrected order; any future C version of this or a
   neighboring leaf must too.
2. **The extended-test miss joins the plain shift with the cell
   still loaded.** `bez r0, 0xE38` targets the shift itself, not
   the alternate loads at `0xE34/0xE36` (those run only on the
   mask-alternate path). The oracle models the join without a
   re-read; stock-side traces confirm zero reads between the
   extended test and the `store4` block on that path.

## 4. Reviewed-form deviations from stock (all battery-proven)

- `addi`-fold of the entry-byte `-1` gate (`(b6+1)==0`, exact for
  sign-extended bytes), saving 2 bytes.
- Retained table bases materialized with `movih`/`ori` (the
  assembler places literal pools only at the section end, so an
  `lrw` pool cannot sit inline as in stock), same 6 bytes per site.
- The one unreachable stock padding halfword after the first
  indirect jump is omitted to hold the envelope; both sides never
  fall through that jump.
- A first-attempt `or`-fold of the plain gate was WRONG
  (`(bit|sel)==0` means AND; stock stores on OR) and was caught by
  the battery on its first case; the reviewed form keeps stock's
  two branches.

## 5. Verification

- 8,370 stock/source/oracle cases: full unfiltered access-trace,
  final-RAM, and live-register (`r0/r2/r3/r4/r5/r6/r14/r15`)
  agreement from entry through handoff into retained `0x10000EA0`.
  Table modes direct/entry-0/scan/first-fill-miss; ids 0..25;
  selectors 0/1/`0x8000`; caller r6 pattern/zero; entry bytes
  `-1`/0/edges/sign-extended; select-cell bit pairs; 1-pass and
  4-zero walks. Fill scratch (`r1/r7-r13/r16+`) is trace-compared
  only: the two fill compilations legitimately differ there.
- 13 host tests: interpreter units (indirect jump, `bclri`,
  both shift orders, trap words, push/pop, foreign-call
  rejection), oracle/table-map consistency (dump vs logistics map
  vs reverse maps, unknown-target rejection, battery scale), and
  placement (envelope hash, exact 264-byte fill, alignment, no
  relocations).
- Jump-table contents are pinned against the stock dump
  (`check_tables`: jt1 package `0x1EB0`, jt2 `0x1EF8`) and fail
  closed on drift.
- Excluded (leftover-dependent, branches kept without outcome
  claim): second-fill failures (fill scratch leftovers differ by
  fail kind: stock leaves `r3` = 25/0, the compiled fill its own),
  hence out-of-range ids and id 26+ (their guard edges land on the
  same passthrough/check targets the in-range battery executes).
  The zero status-bit arm is mathematically unreachable
  (`1u<<k` never 0 for `k` in 0..31).

## 6. What remains for CD-001 (5,622 bytes)

Unchanged critical path: the `0x10000EA0` second dispatcher
(~300+ B, jump table at pool `0x1EA8`/`0x1EF4`, extent past
`0x10000F56` not yet mapped) still gates the beacon
(`0x100004D0`), handshake, init, orchestrator (`0x10001DDC`), and
receive-loop regions. The `0x10001378` sweep was mapped this pass
to a 0x1678 call into blocked `0x10001DDC` plus MMIO/jump-table
tails past `0x100016C8` — larger than estimated, still deferred.
The `0x10000C9C` UART-config block is H-class on unregistered
`0x1000046C`/`0x100003BC`. The `0x10001E60..0x10002000` tables
stay retained (compiler layout). Hardware qualification stays
blocked by unavailable physical evidence.
