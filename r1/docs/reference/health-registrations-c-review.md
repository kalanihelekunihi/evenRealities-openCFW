# R1 health event registration and temperature shutdown in C

`native_health_registrations.c` supplies event subscription pairs at `0x4aad0`
and `0x497a4`, temperature mode-topic registration at `0x4b698`, default-mode setup
at `0x4a59c`, and temperature stream shutdown callback `0x4bd60`. All five are
ordinary C with no new assembly or RAM globals. The
[review receipt](health-registrations-c-review.json) binds production source/object
hashes, REA bytes/literals, replay artifacts, qualification and normal composition.

The subscription pairs register group 4 before group 1, ignore the first raw
result and preserve the second result. Mode topics register the temperature
shutdown callback for group 4 and the existing C sleep-status controller for
group 3. Default setup calls authorization with `(3,1)` before registering its
group-4 callback, even if authorization reports failure. Every registration uses
the address of the canonical system-thread handle cell, not its current handle
value: stock `0x20006610` corresponds to `&r1_event_system.thread`.

The shutdown callback reads the status byte once. Value 1 returns immediately;
other values walk all three live temperature handle slots in order. Each nonzero
handle is unregistered by name `temp`, then its slot is cleared after the call.
Following slots are read fresh, preserving unregister callbacks that mutate them.
The existing canonical temperature handles remain the sole state owner.

Five deeper callback bodies remain explicit native imports. Their declarations
are pointer-only contracts; this unit does not invoke them or claim their call
ABI has been reconstructed. The temperature shutdown callback and sleep-status
controller use existing C implementations instead of fixed executable pointers.
The fixture normalizes only the reconstructed shutdown callback's pointer identity
when comparing native and C subscriber nodes.

There are 513 paired native/C cases: 96 modeled registration cases, 32 cases
executing the actual subscriber-registration implementations and 385 shutdown
callback cases. Actual list cases compare heap roots/nodes and duplicate handling
across repeated registration, with allocator and locks modeled. Other cases cover
full raw result words, authorization failure, changing thread-handle values,
zero/nonzero handles, fresh-slot mutations, status aliases and null-status faults.
Seven compiled defects are rejected: thread value instead of reference, wrong
second group, early return, missing/early slot clearing, wrong status gate and
wrong default-mode argument. Registration R0, public state, provider arguments and
faults are compared; callee-saved registers, SP, masks and FPSCR are checked.
Shutdown callback R0, other caller-clobbered registers/APSR and private stack
residue are excluded. Deeper subscriber frames differ as already documented for
that provider; registration wrapper depths remain native 8/0 bytes. Physical and
concurrent behavior remain unverified.

All 635 units compile and both relocatable compositions pass without duplicate
strong symbols. All 634 earlier objects remain identical. Four startup imports
are resolved and five callback interfaces exposed, changing application imports
from 172 to 173; bootloader imports remain 34. Manifest checks pass. None of the
five new roots qualifies as exact. The source plan remains at 4,339 source-built
bytes, and a fresh hybrid matches the locked artifact with 641,821 executable
pull-through bytes and 248 resource bytes. Complete source-only linking and
firmware hardware validation remain unfinished.
