# GX8002 UART boot stage-1 time leaf analysis and remaining-code map (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 1,114 source-owned bytes
(vectors/table/traps 264, reset 48, divmod/stub 128, PMU trim bits 72,
polled UART 124, ID/bitmod 42, XIP 256, PMU fill 180). This pass closed
**no further bytes** (`bytes_source_owned` unchanged at 1,114) and
registers nothing: every remaining code leaf in the range is either
blocked on the two unreconstructed dispatchers (`0x10000D98`,
`0x10000EA0`), is a noreturn trap/hang tail that cannot be demonstrated
to return, or cannot fit its stock envelope with an inlined divider.
What this pass lands instead is the identification that unlocks the
range: the `0x100003BC` leaf is the SDK `spl_get_time_ms()`, its
out-of-range callee is the stage-2 `__div64_32`, and a complete
return/hang/blocked map plus `rts` inventory routes the next tranches.
No source files were added; no shared files were touched.

## 1. `0x100003BC` is SDK `spl_get_time_ms()` (identified, not closed)

Raw bytes at package `0x40C..0x44A` (62 B), disassembled with the
CD001-analysis flag recipe:

```
push r15; subi sp,8
r3 = 0xA0400000 (movih 41024)
r0 = 0
r12 = *(r3+4); r3 = *(r3+8)        ; LO, HI
spill (r0=LO, r1=HI) to stack
if (HI == 0) r0 = LO/1000 (divu; result discarded, see below)
r1 = 1000; r0 = sp; bsr 0x100065E4 ; 64-bit divide of the slot
r0 = *(sp); sp += 8; pop r15; bkpt  ; reload, restore, TRAP
```

This is `spl_get_time_ms()` from the pinned NationalChip grus SDK
(`arch/soc/grus/spl/spl_counter.c` at SDK commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`):

```c
timebase_l = readl(GXSCPU_VA_COUNTER_2_VALUE);    /* +0x04 */
timebase_h = readl(GXSCPU_VA_COUNTER_2_ACCSNAP);  /* +0x08 */
do_div(time, 1000);
```

with `GX_REG_BASE_COUNTER = 0xA0400000` (`base_addr.h`) and the
`do_div()` fast path (`(n>>32)==0` inlines 32-bit `/`, else calls
`__div64_32`; `base/include/div64.h`). The stock `bnez HI` + dead
`divu` is exactly the `do_div` fast-path shape; the `bsr` is the
`__div64_32` call. Only the numeric addresses (`0xA0400000`, `+0x04`,
`+0x08`, `1000`) cross the boundary; no SDK text is reproduced anywhere
in this note.

The callee decodes cleanly once the stage-2 load offset is applied
(stage 2: package `0x2850` -> runtime `0x10002800`, so true runtime
`0x100065E4` is package `0x6634`): it is a textbook `__div64_32`
estimate-then-restore loop (`divu` high estimate, `mult` adjust,
`add.64`/`sub.64` shift loop, quotient stored to `(r0)`, `rts`), using
only `{ld.w, st.w, cmphs, mov, movi, bf, bt, divu, mult, tlsli, tlsri,
sub.64, add.64, or, bnez, bhz, cmpne, bez, br, rts}`. It belongs to the
stage-2 image (CD-003 territory), so this item must not claim it.

The leaf never returns: both the `HI==0` path (double `pop`) and the
`HI!=0` path (single `pop`) fall into the trailing `bkpt` (raw bytes
`...0214 9014 0000` confirm `addi sp,8; pop r15; bkpt`, no `rts`), so
the exception vectors trap the core in the shared trap loop. A taken
call into this leaf halts the boot; its in-image callers (`0x10000D6C`,
`0x10000D7E`, inside the `0x10000D98` dispatcher) can only reach it on
paths that are dead on working hardware, else stock could not boot.

## 2. Envelope-fit result: 62 B cannot hold an inlined divider (measured)

Two clean-room C drafts were compiled with the tranche flags (`-Os
-mcpu=ck804ef -mhard-float -ffreestanding -fno-builtin
-ffunction-sections -fdata-sections -fno-tree-loop-optimize`):

- Restoring-division widened from the reviewed `udiv` leaf, inlined:
  **178 B** in one section (the compiler keeps full 64-bit
  div/bit trackers and branchy compares; `bkpt` correctly emitted).
- `do_div`-estimate structure (one `divu`, then a 32-bit-quotient
  restoring loop): **138 B**.

Both exceed the 62-byte envelope (`0x100003BC..0x100003FA`
inclusive of the trapping `bkpt`, which is behavior and must stay).
Outlining the divider is not routable: the helper has no stock
envelope of its own in this range (its bytes live at package `0x6634`,
stage 2), and the builder copies sections into stock envelopes, so an
outlined call would dangle at the `bsr` in the shipped candidate.
Same-section merging (`section` attribute) does not help either: the
floor for head + divider + trap on CK804 is ~70 B even in hand-tuned
assembly, above 62. The drafts were therefore removed from the tree;
the measurements are recorded here so followups do not repeat them.
Closable only by a denser-than-stock hand assembly (not found), by an
envelope-combining tranche with the adjacent `0x100003FC` delay flow
(see section 4), or not at all if the dead-path reading holds.

## 3. Complete `rts` inventory (package `0x50..0x2050` slice)

Decoded with the CD001-analysis recipe. Every `rts` in the range:

| `rts` runtime | Envelope owner | Status |
| --- | --- | --- |
| `0x10000138` | stub (divmod tranche) | source-owned |
| `0x10000174` | udiv (divmod tranche) | source-owned |
| `0x100001B4` | umod tail (divmod tranche) | source-owned |
| `0x100002C0` | get_stored_id (idbit tranche) | source-owned |
| `0x10000388/3A2/3AE/3BA` | pmu set/get bits (pmubits tranche) | source-owned |
| `0x10000598/5BE/634/656` | put/put_sync/try_get/get_char (serial tranche) | source-owned |
| `0x100007C4/802/828/85C` | pmu_fill_desc multi-return (pmufill tranche) | source-owned |
| `0x10001302` | manual frame-restore epilogue of the `0x10001094`-region flow | retained, blocked on `0x100019C0` (see below) |
| `0x1000193E/9BE` | xip_read/xip_write (xip tranche) | source-owned |
| `0x10001DD8` | `0x10001D9C`-flow tail (pool-overlap, see section 5) | retained, blocked on `0x10000D98` |

There is **no** `rts` in `0x10000860..0x10001302`, in
`0x100003FC..0x10000584`, in `0x100001BC..0x100002BC` (init/handshake),
or in `0x10001DDC..0x10001E60`. Those spans chain by fallthrough into
downstream code or end in `bkpt`/infinite poll loops: they are not
separately closable functions.

## 4. Remaining-code map (all retained)

`R` = returns normally, `H` = noreturn (trap/hang/infinite loop, with
the mechanism), `F` = falls into the next region, `B` = blocked on an
unregistered callee. Caller lists are exhaustive over the slice.

| Range (runtime) | Pkg | Size | End | Callees | Notes |
| --- | --- | --- | --- | --- | --- |
| `0x100001BC..1FC` init | `0x20C` | 64 | F/B | `0x1FC`, `0x1DD8`, `0x1378`, stub, `0x2BC`(done), `0x6D8`, `0x640`(done), `0x2C8`, `0x4A4`, serial(done) | live root; closes last |
| `0x100001FC..2AC` + pools | `0x24C` | ~176 | B | `0x4A4`(B), `0x5C4`(B), `0x5A0/620/640`(done) | handshake orchestration |
| `0x100002C8..374` receive loop | `0x318` | ~172 | B | get_char(done), `0x65C`(B) | calls `0x65C` |
| `0x100003BC..3FA` time-ms | `0x40C` | 62 | H(bkpt) | stage-2 `__div64_32` | section 1; dead paths only |
| `0x100003FC..46A` delay | `0x44C` | 112 | F | none (64-bit counter poll at `0xA0400004/8`) | busy-wait matching the `0x3BC` timebase; falls into `0x46C` |
| `0x1000046C..4A0` | `0x4BC` | 56 | H(bkpt) | `0xD98`(B), `0xEA0`(B) | ends `pop; bkpt` |
| `0x100004A4..4CE` | `0x4F4` | ~42 | H(bkpt) | `0xD98`(B) x2 | ends `pop; bkpt` |
| `0x100004D0..57E` beacon | `0x520` | ~180 | H(poll loop) | `0xEA0`(B), udiv/umod(done) | infinite TX-empty-polled transmit of `79` (`'O'`); `br 0x4F2` with per-pass `pop` (SP drifts, no stack use after) |
| `0x100005C4..616` | `0x614` | ~92 | B | `0xD98`(B) x3, `0x4D0`(H) | never resumes past `0x4D0` |
| `0x1000065C..6D2` announce | `0x6AC` | ~118 | F | `0x1BF8`(B), `0x1D9C`(B) | sends `"ready"` via TX polls, then falls into `0x6D8` |
| `0x100006D8..772` handshake | `0x728` | ~150 | H(bkpt) | `0x46C`(B), pmubits(done), `0x5C4`(B), `0x3FC`(H) | `'S'`/`"OK"` (pool `0x4B4F`) matching; success and delay paths both trap |
| `0x10000860..B8E` rail op A | `0x8B0` | ~454 | H(pop-loop) | pmufill(done) | fail paths cycle `0xB4E` (`pop` per pass); pool `0x20002018` at `0xA2C` |
| `0x10000A30..B8E` rail op B | `0xA80` | ~352 | H(pop-loop) | pmufill(done) | same `0xB4E` idiom; single `bsr`, no pools |
| `0x10000B90..C9A` rail op C | `0xBE0` | ~268 | H(pop-loop) | pmufill(done) | same `0xC5E` idiom |
| `0x10000C9C..D98` | `0xCEC` | ~220 | ? | `0x46C`(B), `0x3BC`(H) | needs both |
| `0x10000D98..E9E` dispatcher | `0xDE8` | ~360 | F | `0x46C`(B), `0x3BC`(H), pmufill(done) | jump table at pool `0x1E60`; **falls into `0xEA0`** (no `rts`) |
| `0x10000EA0..?` dispatcher | `0xEF0` | ~300+ | F | pmufill(done) | jump table at pool `0x1EA8`; end not yet mapped |
| `0x10001094..1302` flow | `0x10E4` | ~400 | R(`0x1302`) | pmufill(done), `0x19C0`(B) | manual `r8`-frame epilogue; blocked on `0x19C0` |
| `0x10001378..?` rail sweep | `0x13C8` | 300+ | ? | pmubits(done), pmufill(done) | only registered callees; end/shape is a followup mapping task |
| `0x100019C0..?` | `0x1A10` | ? | ? | `0xD98`(B) | followup mapping task |
| `0x10001BF8/1D9C` postambles | `0x1C48/1DEC` | ~60 each | B/H | `0xD98`(B) | `0x1D9C` executes pool bytes as `addi` (pool `0x20002274` doubles as code; raw bytes confirm) |
| `0x10001DDC..E60` orchestrator | `0x1E2C` | ~150 | B | `0x1094`, pmubits(done), `0xC9C`, `0xA30`, `0xB90`, `0x860`, pmu_bit_modify(done) | sole caller `0x10001678` (XIP-program region); reachability is a followup |
| `0x10001E60..2000` tables | `0x1EB0` | ~416 | data | — | jump tables + `lrw` pools + `"OK"` + cells; **must stay retained**: contents are compiler layout for the retained dispatchers, not derivable from source (byte-copying them would be a C-array violation of the hard rules) |

## 5. Findings for followups

- Stage 1 is substantially SDK `spl/` code: `spl_counter.c`
  (`spl_get_time_ms`, counter-2 register map) matches decoded behavior
  exactly, and the baud/UART shapes match `spl_uart.c`/`uart_configure`
  precedents. The "compile the already-reviewed runtime sources at
  these addresses" strategy from the CD001 analysis is validated for
  the counter leaf and should be tried for the UART leaves next —
  except where envelopes trap (sections 2, 4).
- The `pop`-per-pass idiom (`0x4D0` beacon, `0xA30`/`0xB90`/`0x860`
  fail loops) and `pop`-then-`bkpt` tails (`0x3BC`, `0x46C`, `0x4A4`,
  `0x6D8`) mean large parts of stage 1 provably never return. On
  working hardware the live boot path must avoid them; the live path
  threads init -> handshake-poll leaves -> serial leaves ->
  dispatcher live arms only. A followup should pin the live arms by ID
  (`0xD98` table at package `0x1EB0`, `0xEA0` table at `0x1EF4`).
- Gating order: `0x10000D98` + `0x10000EA0` (+ `0xEA0`'s downstream
  extent to its `rts`) first — every other retained code region calls
  into them. Each is a full-turn-scale tranche (300-400 B with a jump
  table). `0x10001378` (registered callees only) is the best
  medium-term target after the dispatchers.
- `bhz` semantics (low-halfword-zero vs high-halfword-zero) were not
  settled; the stock `__div64_32` normalize loop is the arbiter when a
  future executor implements `add.64`/`sub.64`/`bhz`/`mult`/`tlsri`.
- Verification runs this pass (all read-only, `/tmp` scratch only):
  flag-fixed disassembly of the full slice, raw-byte confirmation of
  the `0x1DD4` pool/code overlap (`74 22 00 20` =
  `0x20002274` = `addi r2,117; addi r0,1`), pool-word survey
  (`0x20002008/2014/2010`, `0x10001E5C`, `0x10001E60`, `0x10001EA8`,
  `0x20002274`, `0x20002478/24B0`, `0x4B4F`=`"OK"`), two C-fit
  compilations (178 B / 138 B vs the 62 B envelope), SDK
  `spl_counter.c`/`div64.h` reads at pinned commit `8bf9ee5`, and the
  exhaustive `bsr`/`rts` census above. No builds, no shared-file edits,
  no hardware access.

## 7. D98 closing attempt: maps corrected, fit floor measured (2026-09-12)

This pass rewrote the deferred D98 draft
(`components/shared/gx8002/runtime_gx8002_uart_stage1_pmudispatch.c`,
still unregistered) and attempted to close the 264-byte envelope. **No
new source-owned bytes** (`bytes_source_owned` stays 1,226); what lands
is two behavioral corrections, a quantified fit floor, and table
ground truth so followups do not repeat the work.

- Dumped both retained jump tables from the stock image (package
  `0x1EB0`: jt1, 18 words for ids 7..24; package `0x1EF8`: jt2,
  19 words for ids 6..24). jt1: 7,8->fill 2 (`0xDB4`); 17,18->16
  (`0xE30`); 20,21->19 (`0xE2C`); 23,24->22 (`0xE28`); all other
  ids passthrough (`0xE54`), including out-of-range ids via the
  `cmphsi/bt 0xE54` guard. jt2: 6,14->`ori 0x8000` (`0xE58`);
  11->`ori 8` (`0xE82`); 13->`ori 0x2000` (`0xE74`); 17->`bseti 16`
  (`0xE7E`); 18->`bseti 17` (`0xE7A`); 20->`bseti 18` (`0xE6C`);
  21->`bseti 19` (`0xE68`); 23->`bseti 20` (`0xE70`); 24->`bseti 21`
  (`0xE88`); every other id, in range or out, to the check arm
  (`0xE8C`: `bclri r4,2`, tailfail when the masked id is 1 or the
  bit is zero, else the store path at `0xE5C`).
- Two bugs in the old draft, both fixed and table-grounded: id 22
  mapped to fill 19 (stock: jt1 sends 22 to passthrough, fill 22;
  only 20,21 take the 19 arm), and in-range ids without a bit arm
  (7,8,9,10,12,15,16,19,22) were sent to the failure tail (stock:
  jt2 sends all of them to the check arm). A read-only checker
  (`/tmp/check_d98_maps.py`, kept out of the tree) mirrors the
  corrected C maps and matches all 37 table entries plus 8
  out-of-range passthrough probes: `map1 mismatches: none (18/18)`,
  `map2 mismatches: none (19/19)`.
- Restructured the C for density (range-pair `(sub-N)<2` map tests,
  `1u<<k` spelling for `bseti`, mutating `id &= ~(1u<<2)` for
  `bclri`, shared store tails) and surveyed flags: 312 B with the
  plain tranche flags, **298 B floor** with `-Os ... -fno-jump-tables
  -fno-guess-branch-probability -fno-cse-follow-jumps -fno-gcse`
  (confirmed from the tree file: section `0x12a`), 368/352 B at
  -O1/-O2, and a 22-option single-flag probe moved nothing else.
  The compiler ignores the `bseti` spelling (zero `bseti`/`bclri`
  emitted; it prefers 32-bit `ori`/`andni`) and re-derives
  id-relative compares from sub-relative source. The ~34 B gap is
  structural: stock spends ~24 B on two `lrw`/`ldr.w`/`jmp`
  dispatches plus 2-byte `bseti`/`ori` arms, while branch
  transliteration of nine bit arms plus five fill arms cannot go
  below ~298 B without emitting layout tables of its own, which the
  single-section-per-envelope builder rule forbids. D98 stays
  deferred; the closing routes remain a denser-than-GCC hand
  formulation that still fits, adjacent-envelope work, or a
  builder rule change for compiler-generated tables (none attempted
  here).
- Documented UB boundary (same exposure as the old draft, unchanged
  semantics on realistic inputs): `1u << entry[4]`, `p >> (b6+1)`,
  `p >> b6`, and `1u << entry[5]` assume non-negative descriptor
  bytes; real fills yield small non-negative bytes (PMU/MCU word1
  `0x8C/0x88/0x01/0x00`), and the closing battery must pin that
  assumption with its table configs.
- Routing note for the followup that owns the next tranche: rail op
  C (`0x10000B90..0xC9A`, 268 B) decodes as one `pmu_fill_desc`
  call plus an MMIO poll body ending in the shared pop-and-check
  spinner at `0xC5E`/`0xC62` (no `rts`; H-class like the beacon).
  Its first pass is deterministic (register-held entry/M-cell
  addresses, exit/loop decided by arg2 vs bit 27 of a fill-derived
  word), while retry passes read drifted caller stack and can only
  be compared on outcome class. It needs ~10 new interpreter ops
  (`zext`, `mvcv`, `blz`, `nor`, high registers r12-r20, ...),
  making it a full-turn-scale H-class tranche gated only on
  registered callees. The `0x10001378` sweep instead reaches past
  `0x10001560`, uses r18, and needs mapping first; `0x100019C0`
  and everything through the orchestrator stay blocked on D98/EA0.

Hardware qualification stays blocked by unavailable physical evidence.

## 6. D98 dispatcher tranche: analyzed and deferred (2026-09-12)

The `0x10000D98` dispatcher (264 stock bytes, `0xD98..0xEA0`,
package `0xDE8..0xEF0`) was fully decoded and drafted
as clean-room C (`components/shared/gx8002/
runtime_gx8002_uart_stage1_pmudispatch.c`, unregistered draft, kept in
tree). Findings for the followup that closes it:

- Structure: jt1 (18 entries at `0x10001E60`, ids 7..24) selects the
  fill id (7,8->2; 17,18->16; 20,21->19; 23,24->22; else passthrough);
  two `pmu_fill_desc` calls (both already source-owned); descriptor-bit
  tests with M10/M14 cell stores; jt2 (19 entries at `0x10001EA8`,
  values 6..24) selects status bits (6,14->0x8000; 11->8; 13->0x2000;
  17->1<<16; 18->1<<17; 20->1<<18; 21->1<<19; 23->1<<20; 24->1<<21;
  every other in-range value falls into the chkarm, which stores
  unless the masked id is 1 or the bit is zero). Both terminal paths
  pop the frame and tail-chain into retained `0x10000EA0` (reset-entry
  precedent: absolute handoff symbol, behavior-preserving).
- Caller dependence (verified by reading, not yet by battery): the
  failure tail re-enters the pop/store sequence with caller registers,
  so its store pointer comes from caller-stack garbage; the normal
  paths are deterministic. A closing battery must treat caller r6 as an
  explicit input (constrained to the selector on failure paths) and
  compare failure paths on hang/handoff outcome class, normal paths on
  exact traces. In-range ids without a bit arm go to chkarm (they
  store), not to the failure tail — an early draft that sent them to
  the tail was wrong; the jt2 dump above is the authority.
- Envelope fit (the deferral reason): the if-chain C compiles to 292
  bytes against the 264-byte envelope. The gap is structural, not
  slack: stock dispatches through two jump tables (~52 bytes with
  arms); branch transliteration costs ~30 bytes more, and the C cannot
  emit layout tables of its own (retained-table addresses are not
  derivable behavior, and a hand-authored address table would be layout
  rather than reviewed control flow). A followup may try a packed-lookup
  formulation or adjacent-envelope work, but must preserve exact-trace
  equivalence including the caller-garbage failure paths.
- No SDK source for this dispatcher exists in the pinned checkout
  (`spl/` has counter/UART/clock/trim only); it is bespoke uart_boot
  code, so the route stays clean-room C, not upstream vendoring.
- Measurements kept: two-compiler-shape survey of the second id map,
  the `tlsl r5,r3,r5` = `1<<fill` idiom confirmation, the
  `(id&~8)==6` compiler reformulation of the `{6,14}` arm test, and the
  `movi r0,0` strength-reduction of the status carry on the
  provably-zero path (all to be re-proven by the closing battery).
