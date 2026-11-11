# R1 wear raw-HR probe lifecycle in C

`native_wear_raw_hr.c` supplies probe startup `0x3d0fc`, teardown `0x4c64c` and
the empty stream callback `0x3d0f8`. The [review receipt](raw-hr-c-review.json)
binds REA stock bytes, production source/object hashes, differential checks,
native initialization, exact qualification and the locked hybrid rebuild.

Startup conditionally registers `raw_hr`/`wearled` with rate 1 and flags 0 and
publishes its returned handle after registration, including zero. It then freshly
loads the timer word. A nonzero timer is rearmed through stock `0x8a59e`, returning
that provider's raw R0; otherwise it creates a 3000-ms timer with teardown as the
callback and context zero, publishes the returned timer and returns it. Registration
may alter timer state, which must be observed by the subsequent fresh load.

Teardown loads the stream handle, unregisters `raw_hr` when nonzero and clears
the handle after the provider returns. It then freshly loads the timer, releases
it when nonzero and clears that word after release. Provider mutations remain
observable in the same order; clearing early would lose the stock behavior.
Teardown and the empty callback have void contracts; their R0 residue is excluded
from behavior comparison. Exact bytes independently establish the empty callback.

The stream and timer own only four-byte words at `0x20006eac` and `0x20006eb0`.
Native RW/ZI initialization runs on poisoned memory with guards, and an independent
RW decoder agrees that all eight bytes start at zero. Surrounding wear state is
not newly owned. Final source-only placement remains unproven.

The fixture passes 1,952 paired stock/C cases, including zero/full-word handles
and provider results, mutations of both cells at each provider boundary and both
interrupt-mask states. It compares provider arguments, callback identities, public
memory, write widths and startup R0, and checks preserved registers, SP, masks
and FPSCR. Seven compiled defects are rejected: wrong period, wrong flags, dropping
a zero returned handle, missing timer clear, stale timer, early stream clear and
wrong rearm return word. Providers remain modeled. Native teardown uses a 16-byte
provider frame versus C 8; private stack residue, caller-clobbered registers and
APSR are excluded. Physical/concurrent behavior remains unverified.

All 640 units compile and both relocatable compositions pass without duplicate
strong symbols; all 639 prior objects are unchanged. The probe-start import is
resolved and `r1_stream_timer_rearm_native` is exposed, leaving imports at 175/34.
Manifest validation passes. Startup's missing inventory size is corrected to 54
code bytes and the empty callback gets its own two-byte row. Qualification rejects
the startup/teardown bodies but selects the empty callback exactly. A fresh hybrid
matches the locked application before canonical promotion of those two bytes.
The plan now has 4,341 source-built bytes, 641,819 executable pull-through bytes
and 248 resource bytes. Complete source-only linking and firmware hardware
validation remain unfinished.
