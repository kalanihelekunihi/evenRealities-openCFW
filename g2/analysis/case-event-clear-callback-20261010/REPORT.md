# CASE deferred event-clear callback

**COMPLETE bounded wrapper:** `vEventGroupClearBitsCallback` at original `0x0800bf84..0x0800bf8c` (8 code bytes) calls the task-context `xEventGroupClearBits` provider with the event group and mask. The callback's return is unused by the timer daemon.

The Cortex-M0+ source compiles. `verify.py` checks authenticated CASE image hashes and compares original/source execution for 24 combinations of event handle, mask and child result. The ordered child arguments and restored SP match. It leaves the task-context clear provider at `0x0800c44c` as a boundary and does not infer deferred event lifetime. `results.json` records all source/compiler/ELF/original identities.

The CASE archive now has 22 objects, 41 provided globals and 15 unresolved names. At least 15 lower provider contracts plus linker/layout/hardware phases remain. Whole-image duration is unknown.
