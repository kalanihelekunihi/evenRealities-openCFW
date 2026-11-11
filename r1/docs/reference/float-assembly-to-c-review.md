# R1 floating point assembly removed from two C routines

`native_health_average.c` now uses a C cast for the unsigned conversion in
`r1_health_storage_average`. Under the manifest's Clang Cortex-M4 hard-float
profile, its 160-byte function section is **byte for byte identical** to the
previous inline-assembly build (SHA-256
`29c26e1b0e8d5869116a1ba00d782b2539ca25f4203218153cc5d4c245eb7d07`).
All 12 relocation offsets, types and symbols also match. The emitted
instruction remains `vcvt.u32.f32`, preserving the target's saturation and
FPSCR behavior in this pinned toolchain. This is a target-code observation;
ordinary C alone does not guarantee out-of-range float conversion semantics
under other compilers.

`native_math_round.c` now expresses three scalar VFP operations in C. A
function-scoped `#pragma clang fp exceptions(strict)` prevents speculative
execution of the unchosen add/subtract branch. The original inline-assembly
and revised C `roundf` builds were run in Cortex-M4 Unicorn environments
against the locked stock `0x3ad68` routine. In **2,225 paired cases**, each
candidate matches stock on returned float bits, FPSCR, SP, and the input to
the modeled lower rounding provider. Cases span signed zero, half boundaries,
finite extremes, infinities, quiet/signaling NaNs, and 2,000 seeded random
bit patterns with varied provider results. The ignored fixture is
`build/r1-health-average-c-probe-20261110/compare_roundf.py`; its receipt is
`roundf-result.json`.

The rejected ordinary C attempt without strict FP exceptions speculated
both arithmetic branches and changed FPSCR side effects. The accepted build
uses conditional VFP instructions. The current R1 manifest has 965 units in
752 files, all built; `make sources-check` and `git diff --check` pass.
The strict bootloader link remains complete with a valid vector. The strict
application report at `build/r1-roundf-strict-pure-c-20261110/app-link/report.json`
still has 37 undefined symbols and 31,432 bytes of flash overflow. The
manifest-source scan now finds 172 `__asm__` occurrences across 44 C files,
including third-party source. Other handwritten assembly boundaries remain.
