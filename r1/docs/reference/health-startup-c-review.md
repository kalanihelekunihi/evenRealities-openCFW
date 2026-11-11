# R1 sensor health startup coordinator in C

`native_health_startup.c` supplies the sensor task's health startup entry at
`0x4a21c` and empty initialization hook at `0x4b33c`. Both are ordinary C with no
new assembly or RAM globals. The [review receipt](health-startup-c-review.json)
binds production source/object hashes, REA bytes, replay artifacts, negative
controls, qualification and the promoted exact source plan.

Startup runs module setup, detection stream setup, handler registration, GoMore
lifecycle initialization with mode zero, event subscriptions A/B, mode topics,
the empty hook, activity enable and default mode setup in that order. It does not
stop or roll back on earlier raw return values. The final provider's complete
return word is preserved. The empty hook has no observable effects and its call
may be removed by the C compiler. Each deeper native entry has an explicit ABI
import; differently shaped generic analysis-plan functions are not used as
substitutes. This reconstruction does not establish successful downstream sensor
initialization.

REA readback includes the sensor task's actual call at `0x925ac`, the coordinator
body, the no-op and final mode entry. The derived frontier's earlier 72-byte
coordinator extent is corrected to its 48-byte decoded body: the tail branch ends
at `0x4a24c`, where the next function begins with a distinct push prologue. The
historical decompiler inventory is not rewritten. A missing frontier entry for
final mode setup at `0x4a59c` is added as an unresolved native binding.

The fixture passes 250 paired native/C cases: 218 coordinator cases and 32 direct
no-op cases. It covers success/failure/high-bit words at every stage, seeded
random full-word provider returns, zero GoMore mode and interrupt masks. All nine
nonempty provider boundaries are modeled, comparing ordered calls, memory and
final R0. Callee-saved integer/FP registers, SP, masks and FPSCR are checked.
The direct no-op comparison includes all integer/FP registers, APSR and public
fixture memory. Other caller-clobbered state and private stack residue are excluded
for the coordinator. Six compiled defects are rejected: missing stage, wrong mode,
early return, masked final result, swapped stages and a nonempty hook. Physical
and concurrent behavior remain unverified.

All 634 units compile and both relocatable compositions succeed without duplicate
strong symbols. All 633 earlier objects remain identical. Resolving the task-facing
startup entry exposes nine deeper native providers, so application imports change
from 164 to 172; bootloader imports remain 34. Manifest checks pass. This is an
explicit dependency expansion rather than closure of the full startup chain.

The two-byte empty C hook passes exact qualification and enters the source plan;
the coordinator does not qualify. Previous plan units/regions remain intact. The
preview hybrid matches the locked artifact before canonical promotion. Current
exclusive provenance is 4,339 source-built, 641,821 executable pull-through and
248 resource bytes. Complete source-only linking and firmware hardware validation
remain unfinished.

The subsequent [registration reconstruction](health-registrations-c-review.md)
supplies four coordinator dependencies and temperature shutdown in C, while
exposing five deeper callback bodies.

The subsequent [accelerometer adapter reconstruction](gomore-accelerometer-c-review.md)
supplies the handlers-register dependency and its actual stream/cache callbacks.

The subsequent [motion-detection reconstruction](motion-detection-c-review.md)
supplies detection-stream initialization, sampling and ring accumulation in C;
classification remains a native dependency.
