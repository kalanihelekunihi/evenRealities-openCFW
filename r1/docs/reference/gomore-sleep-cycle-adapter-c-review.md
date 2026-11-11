# GoMore sleep cycle stage in C, 2026-11-10

`r1/src/application/runtime/native_gomore_sleep_cycle_adapter.c` supplies the
stock `0x60b80` eleven-argument entry. It maps the live time, offset, sample,
activity, quality and output pointers into the existing typed
`gomore_primitives_sleep_cycle_update` owner. The state type now names the
policy-source pointer at offset `0x138`.

The paired replay found and corrected three source-owner differences. The
initial inactive latch checks the timestamp at state `+0xac`, not the
countdown at `+0xb0`. Interval refinement writes its classification at record
byte 29 (`tail[0]`), while the preceding interval-build status is byte 28.
The transition-one path copies eight policy bytes from policy-source `+2`
into state `+0x130`. Strict floating point exceptions on the stage decision
and decimated ring writer prevent Clang from speculating a guarded `0/0`
average or a float-to-int conversion that sets extra FPSCR sticky flags.

The ignored probe at `build/r1-gomore-sleep-cycle-adapter-20261110/` compares
the pinned official R1 2.2.6.0009 stage against the C adapter and GoMore C
owner. **1,096 paired cases pass**: 72 control/countdown cases and 1,024
seeded cases with varied history, activity, stage, time, samples, policy
source bytes, floating point rounding modes and sticky flags. Return, the
four-byte pre-state guard plus 316 state bytes, 32 output bytes, FPSCR, SP,
eight saved integer and sixteen saved floating point registers match. The
cases execute **182 distinct stock instruction starts** in the 578-byte
entry, including both interval transition paths. The replay binds stock
memory-copy/clear primitives and uses an ignored diagnostic ELF for the C
owner; it does not establish physical sensor behavior or source-only execution
of every lower helper. The production adapter's allocated sections (140
bytes) and two relocations exactly match the replayed object; the production
GoMore object also matches its replayed allocated sections (70,056 bytes)
and 1,565 relocations.

The fresh R1-only build at
`build/sources-r1-gomore-sleep-cycle-typed-20261110/report.json` compiles
892/892 application and 82/82 bootloader units without known failures or
duplicate strong symbols. `make sources-check` passes with 974 R1 units,
761 source files and zero unbuilt R1 units. The strict bootloader link is
vector-valid. The strict application receipt at
`build/sources-r1-gomore-sleep-cycle-typed-20261110/app-link/report.json`
has **25 undefined functions**, one fewer than the preceding checkpoint.
Its full flash load exceeds the configured span by **29,096 bytes**, 256 more
than before. The application executable and firmware byte identity remain
unfinished.
