# GX8002 UART boot stage-1 baud-beacon/bring-up source (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 3,414 source-owned
bytes. This pass closes the **baud beacon at runtime `0x100004D0`
(package `0x520`, 180 bytes)** and the **UART bring-up at runtime
`0x100005C4` (package `0x614`, 92 bytes)** as reviewed clean-room
assembly, verified by 148 decoded stock/source/oracle cases plus 16
host tests, and registered as `uart-stage1-beacon` in the experimental
codec builder. **CD-001 is now 3,686/8,192 bytes source-owned; 4,506
bytes remain.**

## 1. What the leaves are

Both are H-class flows that never return: every terminal path of the
called PMU dispatchers pops its frame and falls into the retained
second-dispatcher loop with no `rts` (pmudisp/pmusecond audits), so
the first chaining call already leaves each envelope.

`0x100004D0` (180 B: 174 code + trap word + 4 pool): `push r4-r7,
r15`; `r6` = pool word `0x20002014`; `r4 = r0`; `[base+0x4] = 0`;
`[base+0x10] = 3`; when `r1 != 0`, poll `[base+124]` bit 0 until
clear, then `[base+12] = 3`, `[base+8] = 79`, `pop`; when the base
already equals `0xA0100000`, `(r0) = (17)` into `0x10000EA0`,
otherwise `(r0) = (18)`. Post-chain (unreachable, admitted by byte
identity): the clock/div baud quotient/remainder math through the
reviewed divmod leaves, a second status poll, transmit-block stores,
and a branch back to the first poll. Read as UART block setup plus a
PMU-clock-id handoff; the baud math never executes because the
`0xEA0` cascade never returns.

`0x100005C4` (92 B: 82 code + trap word + 2 pools): `push r4-r5,
r15`; `r5 = r0`; `r2 = [0x20002008]`; `r4 = r1`; when nonzero,
`(r0, r1) = (115200, 0)` into the beacon; otherwise `r3 =
[0x2000200C]`, `r3 = (r3 != 1) ? 0xA0100000 : 0xA0200000` via `inct`,
`[0x20002014] = r3`, then `(r0, r1) = (16, 1), (17, 1), (18, 1)` into
`0x10000D98`, then `(r0, r1) = (r4, r5)` into the beacon.
Post-chain (unreachable): `pop; bkpt`. Read as one-shot UART
bring-up: flag-gated base selection, PMU fills, then the beacon.

Envelope tiling corroborates the boundaries: the beacon starts
exactly where the traptails `blkclr` envelope ends (`0x4D0`), ends
where the serial `put` envelope starts (`0x584`); the bring-up starts
where `put_sync` ends (`0x5C4`) and ends where `try_get` starts
(`0x620`). Pool self-containment was scanned across the full stage-1
span: `0x580` is referenced only from `0x4D2`, `0x618` only from
`0x5C6`, `0x61C` only from `0x5E2`.

## 2. Why assembly, and zero reviewed-form deviations

A C shape was not attempted: both envelopes are dense hand-scheduled
16-bit traffic with inline literal pools ending in a trapping `bkpt`
word, and the transliteration assembles byte-identical to stock on
the corrected first reviewed form (exact 180/92-byte fill, zero
relocations), so there is nothing for C to approximate.

One toolchain finding is recorded for followups: the C-SKY assembler
silently drops internal branches written with absolute address
operands (e.g. `bez r1, 0x10000508` assembles to zero bytes with no
error; a 4-branch repro yields an empty `.text`). All internal
branches therefore use symbolic labels; the linked encodings match
stock exactly. No SDK text is reproduced and no SDK register map is
used: every cell, base, offset, id, and constant is a numeric
immediate observed in the decoded stock flow.

## 3. Verification

- 148 stock/source/oracle cases (100 beacon: 5 register-seed
  patterns x 2 bases x 5 poll scripts x 2 cell inits; 48 bring-up: 4
  seed patterns x 3 flag values x 4 select words): byte identity of
  both full envelopes, plus full unfiltered access-trace, final-RAM,
  and live-register (`r0-r7`, `r12`, `r14`, `r15`) agreement from
  entry through the chaining call, including the exact chain target
  (`0xEA0` with id 17/18; `0xD98` with (16,1); beacon with
  (115200,0)). The beacon battery covers the r1-skip path, the
  id-17 arm (base `0xA0100000`), and 1-4 deep poll scripts; the
  bring-up battery covers both chain targets and both base-select
  outcomes. Post-chain div/mod bodies are qualified by the reviewed
  divmod tranche and never stepped into; the dispatcher cascade past
  the chaining branch is qualified by the pmudispatch/pmusecond
  batteries.
- 16 host tests: prefix-model chain state for both leaves
  (hand-computed regs and exact traces, including the r1-skip frame
  accounting and the `inct` base select), executor units (push spill
  order, `inct` taken/not-taken, `bseti` 115200 synthesis,
  foreign-call rejection, unmapped-access trap, post-call-op
  refusal), battery scale/entry coverage, baseline report match, and
  placement (envelope SHAs pinned, linked sections exact-fill,
  byte-identical, aligned, no relocations).
- The retained `0x10000EA0` head executes identically on both sides
  and is never stepped into; the stock-side noreturn claim rests on
  a whole-envelope scan (no `rts` in `0x10000EA0..0x10001094`).

## 4. Registration

`uart-stage1-beacon` in `tools/build_gx8002_source_candidate.py`
(`beacon.elf`, `gx8002-uart-stage1-beacon-verification.json`) plus
the `gx8002-source-candidate` test list in `g2/Makefile`. No
experimental-manifest pin change: the manifest does not pin
per-tranche stage-1 providers.

## 5. What remains for CD-001 (4,506 bytes)

Unchanged critical path minus this tranche: the 24-byte retained
`0x10000EA0` head (inline-pool toolchain change), `0x100005C4`'s
callers aside (now closed), the announce (`0x1000065C`)/handshake
(`0x100006D8`)/init (`0x100001BC..0x100002AC`)/receive
(`0x100002C8..0x10000374`) regions, the `0x10001094` flow (blocked on
`0x100019C0`), the `0x10001378` sweep, the orchestrator
(`0x10001DDC..0x10001E60`), and the `0x10001E60..0x10002000` tables
(retained compiler layout). Hardware qualification stays blocked by
unavailable physical evidence.
