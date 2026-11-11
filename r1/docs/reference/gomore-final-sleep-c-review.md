# R1 final sleep serialization and publication in C

`r1/src/application/runtime/native_gomore_final_sleep.c` supplies the
native serializer at stock `0x8fa3c` and publisher at `0x4a704`. It reads the
88-byte native workspace, counts compact stage runs, allocates a public
record, obtains the temperature estimate from the C trimmed-median provider,
serializes through the C GoMore record provider, applies the C sleep-drop
guard, publishes event 13 when accepted, and releases the record. The native
logging and event interfaces are source backed. No stock executable bytes
or assembly are embedded in this unit.

The ignored fixture at `build/r1-final-sleep-probe-20261110/compare.py` runs
stock and compiled C in Cortex-M4 Unicorn environments. It uses the actual
stock and C serializer, stage encoder, and trimmed-median code, while modeling
allocation, clearing, logging, event publication, and the sleep-drop guard.
**912 paired cases** agree on provider events and arguments, complete
allocation bytes, event bytes, and the 106-byte temperature state. Cases cover
wire types 0/1/2; empty, short, 63/64/65/130-length, alternating and random
valid stage arrays; allocation success/failure; guard accept/drop; log modes
0/1/2/4/7; temperature sample counts 0/11/12/13/49/50; negative start
timestamps; and finite, negative, infinite and NaN float inputs. The result
is in `result.json`, bound to the locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

The stock encoder has a high-bit stage edge case: when the first signed stage
byte has its high bit set, it emits a phantom initial run and writes one byte
past its requested allocation. The C implementation preserves the resulting
wire record while allocating one extra byte. **12 additional paired cases**
with high-bit stage values agree on event bytes and temperature state; their
allocation request differs by the one safety byte when the first stage has
its high bit set. The normal 0–3 stage domain uses the stock allocation size.
This is an intentional behavior difference and does not establish byte identity
or physical behavior. Provider mutation and interrupt interleavings remain
outside the fixture.

## Size profile follow-up, 2026-11-10

The manifest now builds this unit with `-Oz -mno-global-merge`. Its two
exported functions, undefined imports, and Arm ABI attributes agree with the
prior `-Os` object, except for the expected optimization-goal tag. Allocated
object sections are 336 bytes smaller. The ignored replay at
`build/r1-final-sleep-oz-replay-20261110/compare.py` relinks the new object
with the unchanged GoMore primitive object and rechecks all 912 paired cases
and 12 high-bit edge cases against the locked stock image. Its result is in
the adjacent `result.json`.

The full 975-unit R1 source build and strict bootloader link pass. The strict
application still has 24 undefined functions; its full flash load exceeds
capacity by 28,072 bytes, 352 fewer than the preceding source build. The
new receipts are `build/sources-r1-final-sleep-oz-20261110/report.json` and
`build/sources-r1-final-sleep-oz-20261110/app-link/report.json`. The earlier
965-unit checkpoint above is historical.

The manifest has 965 R1 units across 752 files, all built, and
`make sources-check` passes. The R1 source build compiles 883 application
and 82 bootloader units without failures or duplicate strong symbols. The
strict bootloader link passes with a valid vector. The strict application
report at `build/r1-final-sleep-c-revised-20261110/app-link/report.json`
resolves the final-sleep import but still has **37 undefined symbols** and
**31,432 bytes** of flash overflow (24,504 bytes in ld's narrower region
diagnostic). `git diff --check` passes.
