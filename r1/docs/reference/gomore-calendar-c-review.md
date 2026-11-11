# R1 native calendar conversion in C

`native_gomore_calendar.c` implements the 176-byte routine at `0x59cb0` in
ordinary C. The [receipt](gomore-calendar-c-review.json) binds REA code/literals,
production hashes, independent date checks, paired replay, rejected defects,
qualification and builds. No assembly, RAM or imports are added.

The interface takes unsigned epoch seconds and an output pointer. It writes
exactly thirteen bytes in native order: zero halfword at offset 6, input word
at 0, second byte at 12, minute at 11, hour at 10, year halfword at 4, month
at 8 and day at 9. Month is **one-based** and also returned in R0; this is not
the portable helper's boolean return. Bytes outside those writes survive.
There are no pointer guards. The integer Julian/Gregorian calculation uses
the recovered constants and unsigned arithmetic over the full input range.
Upstream timezone adjustment remains upstream; this function adds no locale
or daylight-saving policy.

**186,908 direct stock/C comparisons** pass against an independent Python UTC
Gregorian oracle. The corpus includes both ends of every one of the **49,711
unsigned epoch days**, every second in the first day, seeded arbitrary times,
unaligned output offsets and end-of-SRAM cases. Gregorian leap boundaries,
including 2000 and nonleap 2100, are covered. All record bytes, exact write
order/width, partial fault writes, completed month returns, guarded SRAM,
preserved integer registers, SP, masks and FPSCR are checked. There are
**32 matching faults**. Aggregate observations are hashed rather than retaining
hundreds of thousands of repeated guarded records.

Another **4,936 stock/C cases** run the actual C interval builder with actual
C calendar, clear and movement. Calendar fields are verified before the
controlled return-boundary mutations used to test capture/reload behavior.
There are 4,931 actual calendar calls and eight matching faults in this replay.
The builder's independent scalar/history/rational oracles remain active.

A further **2,152 stock/C cases** run the actual C engine, compose, build,
refinement, calendar, descriptor merge, setter and memory routines. This
isolated engine ELF has **no undefined symbols and no provider replacements**;
its 1,476 calendar calls execute the compiled converter. The C replay rejects
execution in stock ROM. Controlled mutations after actual providers return
remain part of the harness. It includes 32 matching faults. This closes the
calendar dependency in the tested computational graph, not the full firmware.

Total: **193,996 routine pairs, 72 faults and 193,924 completed returns**.
Private stack identity, caller-clobbered state and interrupted-fault R0 are
excluded. Unaligned outputs are tested in the emulator's normal access mode;
UNALIGN_TRP, physical/concurrent behavior and complete firmware execution
remain unproven. The builder passes an explicitly aligned calendar buffer.

Ten compiled defects are rejected with native counterexamples: century divisor,
leap-quarter arithmetic, zero-based month, wide seconds store, reordered initial
stores, signed epoch division, boolean return, wide year store, wrong month
pivot and twelve-hour output.

All **672 units** compile and both relocatable compositions pass without
strong-symbol duplicates. All **671 previous sources/objects** remain unchanged.
Resolving calendar adds no imports, leaving **163 application / 34 bootloader
imports**. The interval engine's reachable providers now execute from source
in the isolated replay; other firmware dependencies remain unresolved.

Instruction qualification rejects the compiled bytes. The canonical plan stays
at 4,369 source-built bytes, 641,791 executable pull-through bytes and 248
resource bytes. The fresh hybrid application matches the locked artifact
through pull-through. Complete source-only firmware linking, byte-identical
rebuilding, context initialization and physical hardware validation remain
unfinished.
