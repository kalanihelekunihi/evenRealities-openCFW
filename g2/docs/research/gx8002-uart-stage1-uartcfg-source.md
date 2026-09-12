# GX8002 UART boot stage-1 UART-configure block source (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 2,630 source-owned
bytes. This pass closes the **`0x10000C9C` UART-configure envelope
(package `0xCEC`, 208 bytes: 204 of body plus the 4-byte chaining
branch)** as reviewed clean-room assembly, verified by 1,500 decoded
stock/source/oracle cases plus 15 host tests, and registered as
`uart-stage1-uartcfg` in the experimental codec builder. **CD-001 is
now 2,838/8,192 bytes source-owned; 5,354 bytes remain.**

## 1. What the leaf is

The straight-line register program at `0x10000C9C..0x10000D68`
(package `0xCEC..0xDBC`):

```
r3 = [r0]; if (r3 != 0) goto body; r0 = 0
body: r3 = 0xA0005000 (lrw pool)
[r3+0x3C] &= ~2; [r3+0x3C] &= ~1
r2 = [r0]; if (r2 == 0) chain
[r3+0x1C] = ([r3+0x1C] & -64) | [r0+0x10]
[r3+0x20] = ([r3+0x20] & -256)
[r3+0x24] = ([r3+0x24] & -32)
[r3+0x20] |= byte [r0+0x14]
[r3+0x24] |= ([r0+0x14] >> 8) & 0x1F      ; zext 12,8
[r3+0x28] = ([r3+0x28] & -8) | [r0+0x24]
[r3+0x2C] = ([r3+0x2C] & -128) | [r0+0x18]
[r3+0x30] = ([r3+0x30] & -8)
[r3+0x30] |= ([r0+0x2C] & 7)
[r3+0x30] &= ~0x30
[r3+0x30] |= ([r0+0x20] << 4)
[r3+0x3C] &= ~4
[r3+0x3C] |= (([r0+0x1C] << 2) & 4)
[r3+0x3C] |= 2; [r3+0x3C] |= 1
chain: bsr 0x1000046C                       ; noreturn into retained flow
```

No callee besides the terminal chaining branch; no polls, no loops,
no literal-pool dependency in the reviewed form. Entry `r1`/`r4`-`r6`
are never read by the body. The `0x10000D6C..0x10000D98` tail (two
`bsr 0x100003BC` time calls around a status-bit spin, the two pool
words, `bkpt`) stays retained stock: it is unreachable past the
noreturn chaining branch on both sides.

## 2. Why assembly, and the two reviewed-form deviations

The body is dense hand-scheduled 16-bit read-modify-write traffic
with an inline literal pool; GCC -Os cannot reproduce the density and
materializes large bases through its own end-of-section pool. Both
deviations are battery-proven:

- Stock `lrw r3, [pool]` for the base (pool word at package `0xDE0`,
  inside the retained dead tail) is materialized with `movih`/`ori`
  (pmudispatch-leaf precedent; the assembler places pools only at the
  section end).
- The stock frame is dropped and the dead entry `mov r4, r1` is gone:
  the body reads no stack slot and no r4-r6, so `push r4-r6, r15`,
  the zero-path `pop`, and the dead move are omitted (exact-fit: 208
  compiled bytes into the 208-byte envelope, zero fill). The removed
  stack-window traffic is excluded from trace/RAM comparison (mdelay
  precedent) while the source entry sp is aligned per path
  (`SP0 - 16` on the pushed nonzero-entry-word path, `SP0` on the
  balanced zero path) so sp matches exactly at the chain. Stock r4 at
  the chain holds entry r1 versus the passthrough seed in the
  reviewed form; r4 is implementation-defined there and dead
  downstream (retained `0x1000046C` opens with `push r4-r5, r15`
  before any read, pinned by a host test). Entry-r1 variation stays
  in the battery to prove trace independence.

## 3. Verification

- 1,500 stock/source/oracle cases: full access-trace (outside the
  stack window), final-RAM (outside the window), and live-register
  (`r0/r1/r2/r3/r5/r6/r14/r15`) agreement from entry through the
  chaining branch. Entry base descriptor-RAM vs address 0; entry
  word 0/one/all-ones/`0x12345678`/pattern; `0x14` word over
  byte-lane and zext(12,8) selectors; five descriptor-word sets;
  three MMIO seeds; two entry-r1 seeds.
- 15 host tests: interpreter units (base materialization, zext
  field, shift/bit ops, negative-mask subi, byte lane, push/pop,
  chain link-register clobber, foreign-call rejection, trap),
  battery model (scale, chain/program corner coverage, r1 trace
  independence, 0x46C save-before-read pin), and placement
  (envelope hash, exact 208-byte fill, alignment, no relocations).
- The independent oracle restates the RMW order per group from the
  decode (including descriptor-before-MMIO in the `0x30 & 7` and
  final-`0x3C` groups, caught by the battery during construction).

## 4. What remains for CD-001 (5,354 bytes)

The closed block hands off to retained `0x1000046C` (still blocked
on the `0x10000EA0` second dispatcher), and its dead tail stays
retained (blocked on the `0x100003BC` time leaf). Unchanged critical
path after this pass: the `0x10000EA0` dispatcher (~500 B envelope
with clock arithmetic), the `0x10001094` flow (live 132 B prefix up
to its `bsr 0x100019C0`), the `0x10001378` sweep, the handshake/init/
beacon/receive regions, the orchestrator, and the `0x10001E60..`
tables (retained compiler layout). Hardware qualification stays
blocked by unavailable physical evidence.
