# R1 default activity-mode transition callback in C

`native_health_default_mode.c` implements callback `0x4aa64` in ordinary C,
reusing the authenticated activity-mode byte. The
[receipt](health-default-mode-c-review.json) binds REA bytes, production hashes,
direct and C wake-chain comparisons, rejected defects, qualification and builds.
Decoded code through `0x4aa91` establishes **46 bytes**, replacing the former
unknown frontier extent. No RAM or assembly is added.

The callback returns unless the incoming event byte is zero and activity mode
is **exactly 1**. It clears activity mode **before** reporting temperature sleep
status zero, then invokes the GoMore force-wake routine, then publishes event
kind **12**, pointer **to the shared activity-mode byte**, length **1**. Neither
provider return failures nor provider changes to that mode introduce another
guard or clear. The publisher therefore sees the latest shared byte, including
changes made during wake processing. Its tail-call entry preserves stock SP.

Validation passed **3,136 direct paired cases** and **3,456 cases executing the
actual C GoMore wake routine, EABI memory clear and musl memset**. Direct cases
cover every event and mode byte, aliases with mode/adjacent storage, both
interrupt-mask states and provider changes. Integration covers both wake heap
allocation failures, sensor flags, authorization flags, changing log modes,
dispatch/final-record behavior and mutations to the published mode from lower
providers. The temperature report and lower interval/authorization/heap/logging/
event providers remain modeled; existing C implementations are not all invoked
in this fixture.

There are **6,576 completed cases and 16 expected invalid-event faults**. Faults
occur before providers or mode writes. Comparisons check provider order,
arguments and state, the single-byte early clear, saved integer/FP registers,
SP, masks, FPSCR and guarded SRAM. Void R0, caller-clobbered registers/APSR and
private stack bytes are excluded. Seven compiled defects were rejected:
inverted event guard, broad mode guard, late clear, omitted wake, private
snapshot payload, wrong event kind and wrong event length.

All **660 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **659 previous objects** are unchanged; the
registration source only adopts the recovered callback prototype. Resolving
the callback adds no imports, leaving **166 application / 34 bootloader imports**.
No exact-qualified body is selected. The canonical plan remains at 4,369
source-built bytes and the fresh hybrid matches the locked application through
executable pull-through. Final source-only linking, full provider behavior,
concurrency and physical activity/sleep transitions remain unproven.

The subsequent [sleep report/shared-state review](algo-sleep-report-c-review.md) now supplies the report and consolidates activity mode with the canonical sleep/wake state at 0x20006ed4. The updated getter/default-mode callers and mixed transitions are replayed there.
