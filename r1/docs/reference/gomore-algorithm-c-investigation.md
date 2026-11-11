# GoMore algorithm coordinator C investigation

This is the pre-integration checkpoint. The subsequent [C review](gomore-algorithm-c-review.md) records consolidated ownership and production-object replay.

An experimental typed C candidate for stock `0x5ff94` now compiles under strict
GCC floating-point settings. The [receipt](gomore-algorithm-c-investigation.json)
binds REA's complete 1,606 bytes/pseudocode, instructions, stage descriptors,
source/object and replay. Production still imports this coordinator; no source
manifest or canonical image selection changes at this checkpoint.

The candidate uses sixteen explicit typed provider calls. Live control zero
uses supplied delta, one uses delta one and is cleared after the call, two is
changed to three without dispatch, and other values suppress dispatch. A
captured control governs the post-call clear even if the provider mutates it.
Low result bytes are published, followed by the existing marker/no-op. Stock's
marker is the exact `bx lr` leaf; it executes on both replay paths. Its
caller-clobbered argument register values are excluded because the leaf has no
effects. Final raw return is context+0x37fd, confirmed by instructions/replay.

The activity-window provider `0x6138c` receives float delta in S0 and pointers
in R0..R3: context+0x33d8, context+0x88, context+0x38, context+0x1c0. The generic
stage descriptor currently names 0x30 instead of the native 0x88 input offset.
That generic source has not been changed here; consolidation must resolve its
ownership and callers explicitly rather than wire the wrong descriptor in.
Other providers receive their native integer and outgoing stack arguments.

**4,512 native/C cases** pass against an independent ordered-call and state
oracle. Coverage includes every one of 256 control values at each stage, delta
extremes, four FP rounding modes, seeded mixed controls, provider changes to
current/future controls and a provider changing rounding mode before activity
conversion. Provider-entry/marker FPSCR, stack argument values, low-byte statuses,
context effects, final raw return, SP and saved integer/high-FP registers agree.
The unsigned-to-float oracle implements rounding with integer arithmetic.

Eight independently compiled defective variants are rejected: wrong activity
input pointer, forced-one delta, dispatching control two, retaining control two,
rereading mutated current control, wrong status offset, signed activity-delta
conversion and incorrect raw return. Compilation failures are not counted.

Nine control-boundary native/C cases also agree, including eight unmapped-read
faults and one completed boundary case. These compare invalid access address/size,
earlier status writes and completed raw return; private stack writes are excluded.
The work providers are not reached in this boundary fixture.

Actual native/C host adapters, resamplers, wrappers, filters, interpolation and
coordinator pass **334 integration cases**, including **nine fault cases** and
**3,259 modeled calls**. The fixture compares both full 0x3ae4-byte context views,
exact host scratch pointers, provider arguments/FPSCR, final state and return.
Logging and sixteen lower stage providers remain modeled; stock clear, move and
marker execute. This proves interaction at those boundaries rather than a
completely source-executed graph. Old modeled interpolation mutation duplicates
remain excluded from this fixture.

All sixteen work providers are still modeled. Provider SP equality, private
stack aliasing and physical behavior remain unproven. The candidate does not add assembly or persistent RAM.
The existing generic orchestrator is still the production generic owner; it must
be consolidated before promoting this candidate. Lower-provider C completeness,
physical execution, source-only final linking and byte identity remain separate
requirements. Experiments remain under `build/goal-r1-gomore-algorithm-c/`.
