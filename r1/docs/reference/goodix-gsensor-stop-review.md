# Goodix accelerometer stop consumer in C

REA confirms stock `0x6f9d4` loads the stop word at `0x2002fd2c`, returns when
null and otherwise tail-dispatches through that word. `r1_goodix_gsensor_stop`
now consumes the shared C callback table introduced by the registration work.
A required tail call preserves the caller's stack pointer and return address.
The old generic `goodix_primitives_call_hook` body and declaration, previously
mapped to this entry, are removed: accepting a hook argument and returning a
Boolean did not represent the stock shared-state consumer.

Seventy-two paired stock/C cases (144 executions) compare the live stop-slot
word read, callback selection, unchanged table/canaries, preserved registers,
stack and interrupt masks. Cases include null and two callback targets, varied
incoming argument registers and interrupt masks. Each modeled callback checks
that its stack pointer and return address are the original caller's values.
All 1,029 registration regression cases pass against the current object.
A deliberate start-slot variant fails the stop-slot read oracle with a mapped
start callback and a null stop callback.

The current C body is 16 bytes versus 12 stock instruction bytes. It uses CBZ
where stock uses CMP/branch, so flags differ and are explicitly excluded from
this void-callback behavioral probe. Caller-clobbered argument registers,
arbitrary invalid targets and callback-specific hidden register conventions
are also outside its proof. This is not instruction or whole-image identity.

The normal report `build/sources-goal-r1-goodix-gsensor-stop/report.json`
compiles 566 R1 units without failures or duplicate strong symbols. Imports
remain 199 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-gsensor-stop-review.json) binds REA, owned source,
negative control, execution probes and normal build by hash. The canonical
source plan and G2 gates remain unchanged.

No external registration caller was found by the current REA reference query,
raw Thumb call search or literal pointer scan. This does not prove the routine
unreachable: computed calls or dynamically installed pointers remain possible.
Concrete sample callback targets/signatures, cache-start logging/frame behavior,
startup placement, interrupt interleavings, physical accelerometer behavior
and full source-only byte identity remain unverified.
