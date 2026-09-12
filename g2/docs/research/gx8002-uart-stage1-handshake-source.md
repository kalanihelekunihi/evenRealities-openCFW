# GX8002 UART boot stage-1 handshake-leaf source (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 3,810 source-owned
bytes. This pass closes the **UART handshake at runtime `0x100006D8`
(package `0x728`, 168 bytes)** as reviewed clean-room assembly,
verified by 15 decoded stock/source/oracle cases plus 13 host
tests, and registered as `uart-stage1-handshake` in the experimental
codec builder. **CD-001 is now 3,978/8,192 bytes source-owned; 4,214
bytes remain.**

## 1. What the leaf is

An H-class flow that never returns: the first (and only reachable)
transfer is the chaining call into the reviewed rail-configure tail
(`0x1000046C`, traptails tranche), which runs straight-line into the
reviewed first PMU dispatcher (`0x10000D98`, noreturn per the
pmudisp audit: every terminal path pops its frame and falls into
the retained second-dispatcher loop with no `rts`). The post-chain
tail -- two PMU bit reads, two bring-up calls, the "GET"/"OK"
exchange, the delay call, and the pop-trap -- never executes and is
admitted by byte identity.

`0x100006D8` (168 B: 154 code + trap word + 12 pool, `pop` at
`0x770`, `bkpt` at `0x772`): `push r4-r9, r15`; `(r0, r1)`
unchanged into `0x46C`. Post-chain (unreachable, admitted by byte
identity): `(r0)` into `0x3A4` (pmu get bit0), continue only when
`r0 == 1`, else the alt arm; `(r0)` into `0x3B0` (pmu get bit1),
same 1-gate; `(r0, r1)` = (1, 0), or (0, `[0x20002010]`) on the alt
arm, into `0x5C4` (bring-up); TX-empty-polled (`[base+20]` bit 6)
stores spelling "GET" (71, 69, 84); RX-ready poll (`[base+20]`
bit 1); on empty with zero retry budget `(r0) = (1)` into `0x3FC`
(mdelay) and retry; on a received byte, `zextb` + compare against
the expected sequence (`'O'` = 79 first, then bytes of the retained
table at `0x10001E5C` = "OK"); mismatch advances and retries,
full match or zero expected byte pops the frame into `bkpt`. Read
as rail setup plus a "GET"/"OK" boot handshake that only runs if
the dispatcher cascade ever returned.

Envelope tiling corroborates the boundaries: the leaf starts
exactly where the announce pool ends (`0x6D8`) and ends exactly
where the source-owned pmufill leaf starts (`0x780`). Pool
self-containment was scanned across the full stage-1 span: the pool
words `0x20002010`/`0x20002014`/`0x10001E5C` at `0x10000774..0x7F`
are referenced only by the `lrw` sites at `0x6F8`/`0x708`/`0x70E`.
The single caller is init (`0x10000200`-region, still retained).

## 2. Why assembly, and zero reviewed-form deviations

A C shape was not attempted: the envelope is dense hand-scheduled
16-bit traffic with a literal pool and a trapping `bkpt` word, and
the transliteration assembles byte-identical to stock on the
corrected first reviewed form (exact 168-byte fill, zero
relocations), so there is nothing for C to approximate. The one
correction during review: the first TX poll loops to `0x718` (status
re-read only), not to the `0x712` base re-read -- caught by byte
comparison before any battery ran. Internal poll branches use
symbolic labels (the C-SKY assembler silently drops branches
written with absolute address operands; beacon-audit toolchain
finding). No SDK text is reproduced and no SDK register map is
used: every cell, table address, offset, and constant is a numeric
immediate observed in the decoded stock flow.

## 3. Verification

- 15 stock/source/oracle cases (5 register-seed patterns x 3 stack
  bases): byte identity of the full envelope, plus full unfiltered
  access-trace, final-RAM, and live-register (`r0-r9`, `r12`,
  `r14`, `r15`) agreement from entry through the chaining call,
  including the exact chain target (`0x46C`) with entry registers
  preserved and the return address (`0x6DE`). The live prefix
  performs zero MMIO traffic (seven frame pushes only). The
  dispatcher cascade past the chaining branch is qualified by the
  reviewed traptails/pmudispatch/pmusecond batteries; the
  post-chain PMU/bring-up/delay calls by their own batteries.
- 13 host tests: prefix-model chain state (exact regs and push
  trace, shifted-stack variant), executor units (push spill order,
  foreign-call rejection, unmapped-access trap, post-call-op
  refusal), battery scale/entry coverage, baseline report match,
  and placement (envelope SHA pinned, linked section exact-fill,
  byte-identical, aligned, no relocations, pool words pinned).
- The retained table at `0x10001E5C` is read-only referenced and
  never stepped past; its contents stay retained stock (compiler
  layout, tables-region precedent).

## 4. Registration

`uart-stage1-handshake` in `tools/build_gx8002_source_candidate.py`
(`handshake.elf`, `gx8002-uart-stage1-handshake-verification.json`)
plus the `gx8002-source-candidate` test list in `g2/Makefile`. No
experimental-manifest pin change: the manifest does not pin
per-tranche stage-1 providers.

## 5. What remains for CD-001 (4,214 bytes)

Unchanged critical path minus this tranche: the 24-byte retained
`0x10000EA0` head (inline-pool toolchain change), init
(`0x100001BC..0x100002AC`)/receive (`0x100002C8..0x10000374`)
regions, the `0x100003BC` time helper (H-trap, envelope-fit
measured impossible alone), the `0x10001094` flow (blocked on
`0x100019C0`), the `0x10001378` sweep, the `0x10001BF8` rail
program, the orchestrator (`0x10001DDC..0x10001E60`), and the
`0x10001E60..0x10002000` tables (retained compiler layout).
Hardware qualification stays blocked by unavailable physical
evidence.
