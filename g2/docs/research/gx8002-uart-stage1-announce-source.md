# GX8002 UART boot stage-1 announce-leaf source (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 3,686 source-owned
bytes. This pass closes the **UART announce at runtime `0x1000065C`
(package `0x6AC`, 124 bytes)** as reviewed clean-room assembly,
verified by 30 decoded stock/source/oracle cases plus 15 host
tests, and registered as `uart-stage1-announce` in the experimental
codec builder. **CD-001 is now 3,810/8,192 bytes source-owned; 4,382
bytes remain.**

## 1. What the leaf is

An H-class flow that never returns: the first (and only reachable)
transfer is the chaining call into the retained rail-program entry
`0x10001BF8`, whose body runs straight-line push/movs into the
reviewed first PMU dispatcher (`0x10000D98`, noreturn per the
pmudisp audit: every terminal path pops its frame and falls into
the retained second-dispatcher loop with no `rts`). The post-chain
tail -- a polled "ready" transmit loop, the reviewed rail-postamble
call (`0x10001D9C`), and a pop-return -- never executes and is
admitted by byte identity.

`0x1000065C` (124 B: 120 code + 4 pool, no trap word): `push r4,
r15`; `r4` = pool word `0x20002014`; `r3` = `0xA0100000`;
`r12` = base cell; `[base+0xA8] = 1`; `r3` = 6 preselected, then
`inct` replaces it with `r2` (= 4) unless the base already matches
the first UART; `(r0, r1, r2, r3)` = (entry `r0`, base, entry `r1`,
select) into `0x1BF8`. Post-chain (unreachable, admitted by byte
identity): re-read base, five TEMT-poll gated stores spelling
"ready" (114, 101, 97, 100, 121), the postamble call, `r0` = 0,
`pop r4, r15` (return). Read as rail-program handoff plus a boot
announce that only runs if the dispatcher cascade ever returned.

Envelope tiling corroborates the boundaries: the leaf starts
exactly where the serial `get_char` envelope ends (`0x65C`) and
ends exactly where the retained handshake starts (`0x6D8`). Pool
self-containment was scanned across the full stage-1 span: the pool
address `0x100006D4` is referenced only by the `lrw` at `0x65E`.
The single caller is the retained receive-region `bsr` at
`0x10000328` (which continues past the call -- dead code under the
noreturn chain, same shape as the bring-up's post-D98 tail).

## 2. Why assembly, and zero reviewed-form deviations

A C shape was not attempted: the envelope is dense hand-scheduled
16-bit traffic with an inline literal pool directly following the
pop (no trap word), and the transliteration assembles
byte-identical to stock on the first reviewed form (exact 124-byte
fill, zero relocations), so there is nothing for C to
approximate. Internal poll branches use symbolic labels (the C-SKY
assembler silently drops branches written with absolute address
operands; beacon-audit toolchain finding). No SDK text is
reproduced and no SDK register map is used: every cell, base,
offset, id, and constant is a numeric immediate observed in the
decoded stock flow.

## 3. Verification

- 30 stock/source/oracle cases (5 register-seed patterns x 2 bases
  x 3 rail-control inits): byte identity of the full envelope, plus
  full unfiltered access-trace, final-RAM, and live-register
  (`r0-r7`, `r12`, `r14`, `r15`) agreement from entry through the
  chaining call, including the exact chain target (`0x1BF8`) and
  the select id (6 for `0xA0100000`, 4 otherwise). Both select arms
  and all three rail-control inits are covered. The dispatcher
  cascade past the chaining branch is qualified by the reviewed
  pmudispatch battery; the post-chain postamble call by its own
  battery.
- 15 host tests: prefix-model chain state for both select arms
  (hand-computed regs and exact traces), both-arms-over-inits
  sweep, executor units (push spill order, `inct` taken/not-taken,
  `movih` base synthesis, foreign-call rejection, unmapped-access
  trap, post-call-op refusal), battery scale/entry coverage,
  baseline report match, and placement (envelope SHA pinned,
  linked section exact-fill, byte-identical, aligned, no
  relocations).
- The retained `0x10001BF8` prefix executes identically on both
  sides and is never stepped into; the noreturn claim rests on its
  straight-line push/movs prefix into `0x10000D98` (no branch
  before the `bsr` at `0x1C06`) plus the pmudisp noreturn audit.

## 4. Registration

`uart-stage1-announce` in `tools/build_gx8002_source_candidate.py`
(`announce.elf`, `gx8002-uart-stage1-announce-verification.json`)
plus the `gx8002-source-candidate` test list in `g2/Makefile`. No
experimental-manifest pin change: the manifest does not pin
per-tranche stage-1 providers.

## 5. What remains for CD-001 (4,382 bytes)

Unchanged critical path minus this tranche: the 24-byte retained
`0x10000EA0` head (inline-pool toolchain change), the handshake
(`0x100006D8`)/init (`0x100001BC..0x100002AC`)/receive
(`0x100002C8..0x10000374`) regions, the `0x100003BC` time helper
(SDK-identified, uncompiled), the `0x10001094` flow (blocked on
`0x100019C0`), the `0x10001378` sweep, the `0x10001BF8` rail
program, the orchestrator (`0x10001DDC..0x10001E60`), and the
`0x10001E60..0x10002000` tables (retained compiler layout).
Hardware qualification stays blocked by unavailable physical
evidence.
