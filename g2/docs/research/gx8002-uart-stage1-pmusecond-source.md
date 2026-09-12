# GX8002 UART boot stage-1 second PMU dispatcher source (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime
`0x10000000..0x10002000`). Prior passes closed 2,630 source-owned
bytes. This pass closes the **second PMU dispatcher body at runtime
`0x10000EB8` (package `0xF08`, 476 bytes)** as reviewed clean-room
assembly, verified by 2,688 decoded stock/source/oracle cases plus 10
host tests, and registered as `uart-stage1-pmusecond` in the
experimental codec builder. **CD-001 is now 3,106/8,192 bytes
source-owned; 5,086 bytes remain.**

## 1. What the leaf is

The 500-byte envelope at `0x10000EA0..0x10001094` (package
`0xF08..0x10FC`) is a 24-byte retained entry head plus the 476-byte
reviewed body. The head (frame setup, unsigned id-range guard,
retained jump-table dispatch) stays retained stock and executes
identically on both sides:

```
push r4, r15; r14 -= 24
r3 = r0 - 7; T = (r3 >= 19); r4 = r0
bt 0xEC0 if T                 ; out-of-range ids fill with the entry id
r2 = [pool]                   ; 0x10001EF4, inline pool word at 0xEB4
r3 = [r2 + (r3 << 2)]         ; 32-bit ldr.w: slot id-7
jmp r3                        ; plain indirect jump to the slot target
```

The 19-entry retained table (package `0x1F44`, pinned by
`check_tables`) maps slots to arms: slots 0,1 (ids 7,8) restore the
frame and retry with fill id 19; slots 2-9,12,14,15 (ids 9-16, 19,
21, 22) fill with the entry id unchanged; slots 10,11 (ids 17,18)
retry with 16; slots 13,14 (ids 20,21) retry with 19; slots 16,17
(ids 23,24) retry with 22; slot 18 (id 25) retries with 10. The body
itself is one `pmu_fill_desc` call into a 24-byte stack descriptor,
descriptor byte/bit gating, the cell test, the divisor sink, the
descriptor-walk tail with retry arms, the bit-set UART-clock
computation (mult/divu, range clamps), and the entry-word multiplier
path — all joining fill-retry loops that never return (no `rts`;
H-class). The trailing `bkpt` is unreachable padding after an
unconditional branch.

## 2. Why assembly, and the two reviewed-form deviations

A C shape was not attempted: the envelope holds coinciding table
arms the retained dispatch jumps into, so every body address must
match stock exactly, and GCC `-Os` has no reason to reproduce the
dense hand-scheduled 16-bit traffic (pmudispatch precedent). The
compiled section is therefore *not* byte-identical to stock; it
carries two documented, battery-proven deviations at the body entry:
a trace-neutral `nop` position pad (`mov r0, r0`) for the stock dead
`movi r0, 0`, and the fill-failure branch retargeted past it to the
restore block. Admission rests on decoded-trace equivalence, with
arm-address coincidence as corroboration.

The head cannot be transliterated with this toolchain: its table
targets are absolute retained addresses, so the arms must coincide,
while the assembler's literal pools only sit at the section end (no
`.ltorg`), which would displace either the inline table pool or the
arms (measurements recorded in the source header). Closing the head
needs assembler inline-pool support or an equivalent toolchain
change; it is a 24-byte followup.

## 3. The slot-index correction this pass

The battery caught an off-by-one in the first oracle draft: it read
slot id-6 while stock reads slot id-7 (first divergence on id 7:
oracle `read [JT+4]` vs stock `read [JT+0]`, with equal values only
because slots 0 and 1 share the `0xEB8` arm). Root cause was an
analysis disassembly without the CK804EF ELF flags, which fused the
halves of the 32-bit `ldr.w` at `0xEAE` into a pool `.long` plus a
phantom `bt`; with correct flags the dispatch is `lrw`/`ldr.w`/`jmp`
and the index is the post-`subi` register, i.e. id-7. This retires
two stale theories the draft had encoded: the id-25 guard hole (id
25 reads the last in-bounds slot, now battery-covered) and the
postamble audit's "20-entry table for ids 7..26" (19 entries, ids
7..25). The oracle, the ident-keyed arm map, the first-fill map, and
the source header now all state slot id-7; a host test pins the map
against the slot-ordered dump.

## 4. Verification

- 2,688 stock/source/oracle cases (1,824 direct, 672 miss1 with the
  first-fill slot broken, 192 missloop with a retry slot broken):
  full unfiltered access-trace, final-RAM, and live-register
  agreement from entry through the fourth fill call. Entry ids
  0,1,2,6,7,8,9,10,12,15,16,18,19,22,24,25,26,27,31; entry-byte
  -1/0/5/31; direct and selected-cell descriptor words; select-cell
  sweeps; UART-block tuples. Miss chains compare trace and RAM
  exactly but registers only on the fill-independent subset (fill
  scratch leftovers are implementation-defined); fill scratch
  registers compare by trace only.
- 10 host tests: dispatch-slot model (ident map vs slot dump, pinned
  dump, oracle drift rejection incl. the id-25 slot, first-fill ids),
  executor dispatch (indexed slot-load trace shape for slots 0 and
  18, plain-indirect `jmp`, traps), battery scale/coverage (id 25
  present, id-6 miss1 real), and placement (envelope hash, exact
  476-byte fill, alignment, no relocations).
- Jump-table contents are pinned against the stock dump and fail
  closed on drift; the linked section fills its placement with no
  relocations.

## 5. What remains for CD-001 (5,086 bytes)

Unchanged critical path minus this tranche: the 24-byte retained
head above (inline-pool toolchain change), the `0x10000C9C`
UART-config block, `0x1000046C`, handshake/init/beacon, the
`0x10001094` flow (blocked on `0x100019C0`), the `0x10001378` sweep,
the orchestrator, and the `0x10001E60..0x10002000` tables (retained
compiler layout) follow it. Hardware qualification stays blocked by
unavailable physical evidence.
