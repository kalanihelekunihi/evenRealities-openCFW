# GX8002 UART boot stage-1 rail-configure/block-clear trap tails source (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 3,314 source-owned
bytes (3,106 per the pmusecond audit plus the 208-byte uartcfg block
it omitted: its "prior 2,630" predates the concurrently-landed
uartcfg tranche; both envelopes are disjoint and registered, so the
true prior total is 2,838 + 476 = 3,314). This pass closes the
**rail-configure tail at runtime `0x1000046C` (package `0x4BC`, 56
bytes)** and the **block-clear tail at runtime `0x100004A4`
(package `0x4F4`, 44 bytes)** as reviewed clean-room assembly,
verified by 288 decoded stock/source/oracle cases plus 11 host tests,
and registered as `uart-stage1-traptails` in the experimental codec
builder. **CD-001 is now 3,414/8,192 bytes source-owned; 4,778 bytes
remain.**

## 1. What the leaves are

Both are straight-line H-class flows into the PMU rail dispatchers
(first call already leaves the envelope: every terminal path of the
first dispatcher pops its frame and falls into the retained second
dispatcher at `0x10000EA0` with no `rts`, per the pmudisp audit, and
the second dispatcher body is itself H-class per the pmusecond
audit). Callers: `0x46C` from the uartcfg chain, the mdelay
fallthrough, the handshake (`0x100006DA`), and the dispatcher tail;
`0x4A4` from init (`0x10000200`).

`0x1000046C` (56 B: 54 code + trap word): `push r4-r5, r15`;
`r4 = 0xA0400000` (counter block, `movih`); `(r0, r1) = (23, 1)`
into the first dispatcher (`0x10000D98`); `[r4+0x10] = 1` then `0`
with `r0 = 23`; `[r4+0x20] = 1`; `r0 = 23` into the second
dispatcher (`0x10000EA0`); `r3 = 62500`, `rotli r3, r3, 4`
(`= 1000000`); signed `r0 = r0 / r3`, minus 1; `[r4+0x24] = r0`
(reload); `[r4+0x28] = 0`; `[r4+0x10] = 2`; `pop`; `bkpt`. Read as
counter-2 microsecond-tick setup from PMU clock id 23; the reload
math never executes (dead past the first dispatcher call on working
hardware, where the cascade never returns).

`0x100004A4` (44 B: 42 code + trap word): `push r4, r15`;
`r3 = 0xA0500000`; `r4 = 0`; `r2 = [r3+0x40]` (status read,
discarded); `[r3+0x30] = [r3+0x6C] = 0`; `r3 = 0xA0600000` with
`(r0, r1) = (20, 0)`; `r2 = [r3+0x40]` (discarded);
`[r3+0x30] = [r3+0x6C] = 0`; `(r0, r1) = (20, 0)` into the first
dispatcher; `(r0, r1) = (21, 0)` into the first dispatcher; `pop`;
`bkpt`. Two-block control-register clear plus PMU fills ids 20/21.

## 2. Why assembly, and zero reviewed-form deviations

A C shape was not attempted: both envelopes end in a trapping `bkpt`
word and the transliteration assembles byte-identical to stock on the
first reviewed form (exact 56/44-byte fill, zero relocations), so
there is nothing for C to approximate. Cross-envelope dispatcher
calls target linker-assigned absolute symbols (mdelay/uartcfg-leaf
precedent). No SDK text is reproduced and no SDK register map is
used: every base, offset, id, and constant is a numeric immediate
observed in the decoded stock flow.

## 3. Verification

- 288 stock/source/oracle cases (both leaves x 3 register-seed
  variants x 4 x 4 status-read values x 3 clear-cell initials):
  byte identity of both full envelopes, plus full unfiltered
  access-trace, final-RAM, and live-register agreement from entry
  through the first dispatcher call. Both leaves are straight-line
  to the chain (no branches), so every reachable path is covered;
  the post-call tails never execute on either side. All ten live
  registers (`r0-r7`, `r14`, `r15`) match exactly at the chain
  (frames kept, no implementation-defined state); the railcfg
  prefix performs zero MMIO traffic (three frame pushes only).
- 11 host tests: prefix-model chain state for both leaves
  (hand-computed regs and exact traces, including the discarded
  status reads and unconditional clears), executor units (push
  spill order, foreign-call rejection, unmapped-access trap,
  post-call-op/bkpt refusal), battery scale/entry coverage, and
  placement (envelope SHAs pinned, linked sections exact-fill,
  byte-identical, aligned, no relocations).
- The dispatcher cascade past the chaining branch is never executed
  here; it is qualified by the reviewed pmudispatch (8,370 cases)
  and pmusecond (2,688 cases) batteries. `objdump -d` skips the
  zero trap word, so the shape check pins decoded coverage at
  size-2 plus a zero last payload word plus byte identity.

## 4. Registration

`uart-stage1-traptails` in `tools/build_gx8002_source_candidate.py`
(`traptails.elf`, `gx8002-uart-stage1-traptails-verification.json`)
plus the `gx8002-source-candidate` test list in `g2/Makefile`. No
experimental-manifest pin change: the manifest does not pin
per-tranche stage-1 providers.

## 5. What remains for CD-001 (4,778 bytes)

Unchanged critical path minus this tranche: the 24-byte retained
`0x10000EA0` head (inline-pool toolchain change), the beacon
(`0x100004D0`, ~168 B, TX-poll loops, callees now all reviewed),
`0x100005C4`, announce (`0x1000065C`)/handshake (`0x100006D8`)/init
(`0x100001BC..0x100002AC`)/receive (`0x100002C8..0x10000374`)
regions, the `0x10001094` flow (blocked on `0x100019C0`), the
`0x10001378` sweep, the orchestrator (`0x10001DDC..0x10001E60`),
and the `0x10001E60..0x10002000` tables (retained compiler layout).
Hardware qualification stays blocked by unavailable physical
evidence.
