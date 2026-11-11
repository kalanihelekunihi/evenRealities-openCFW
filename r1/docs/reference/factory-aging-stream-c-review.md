# R1 factory aging stream in C, 2026-11-11

`r1/src/application/board/native_factory_aging.c` supplies stock command
`0x629d4`, the one-shot registration at `0x90fac`, and the two accelerometer
callbacks at `0x6f228` and `0x6f304`. The command returns a five-byte status
reply for selector zero, registers the regular listener for selector four, and
registers the calibration listener for selector ten. An active factory mode
returns status `0xff` before selector dispatch. Unknown selectors have no
effect. The regular callback sends the first six sample bytes as a ten-byte
reply, or retains them when factory mode is active.

The calibration callback accumulates at most 100 signed XYZ triples in the
existing twelve-byte factory reset cache. It calculates the three signed
orientation offsets, writes the six-byte result through the cached `nv_r1`
record at offsets 68..73, sends status one, unregisters the listener and clears
the state. The cached-record setter is stock `0x7c8b0` in the existing
`r1/src/application/runtime/native_device_configuration.c` owner. The six-byte
result and first-sample records are source-owned variables corresponding to
native state fields at `0x20006c54` and `0x20006c5a`; the strict source linker
does not place them at those stock addresses.

The ignored host probe at `build/r1-factory-aging-c-20261111/probe.c` passes
all 256 selectors with inactive and active factory mode, stop/unregister,
regular callback send/retain, and five 20-sample batches through completion.
It was compiled with AddressSanitizer and UndefinedBehaviorSanitizer. The
ARM-target syntax check also passes. These tests cover the described paths;
they do not establish sensor timing, flash persistence or physical behavior.

`build/sources-r1-factory-aging-c-20261111/report.json` compiles 935/935
application and 82/82 bootloader units with no known failures or duplicate
strong symbols. The strict application receipt at
`build/r1-link-factory-aging-c-20261111/report.json` has 16 undefined
functions and uses 642,400 of 696,320 flash bytes, with no overflow. The
strict bootloader receipt at
`build/r1-boot-link-factory-aging-c-20261111/report.json` passes with a valid
vector. The repository-wide `make sources` attempt at
`build/sources-r1-pair-geometry-all-20261111/report.json` passed its R1 units
but failed because G2's manifest changed during the build and G2 Apollo main
reported a duplicate strong symbol. `make sources-check` passes. No physical
R1 test or stock byte identity is claimed.
