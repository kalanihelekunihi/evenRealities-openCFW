# Goodix reference-counted release reconstructed in C

`stock_client_release.c` implements stock `0x50be0` in C. REA establishes
selector mapping 1/2/3/4/5/7 to their corresponding counter slots, with selector
6 sharing slot 2. Selectors 8/9 force shutdown; zero and selectors at least 10
return zero without touching policy state. Other accepted selectors return one,
including when their count was already zero.

The new source owns the observed active-mask word (`0x200076c4`), release
callback word (`0x200076c8`) and eight-word counter span (`0x2001e51c`). Native
counter index zero is unused by this routine. The nine mask words match the
stock table at `0x9bb18`. Ownership here does not establish initialization,
acquisition policy or final linked placement.

A nonzero counter decrements once. Only transition to zero clears the mode bit
and opens the bus, stops sampling and closes the bus. The active mask is then
reloaded after those calls. If empty, the routine closes IRQ, drives reset low,
closes the bus again, releases the transport and releases shared-power client
one. It reloads the optional final callback after shared-power release and
calls it with one. The forced path stops mode `0x2000` and executes the shutdown
sequence without changing policy counters/mask or calling that final callback.
Volatile state accesses preserve native widths and ordering.

The probe passes 2,080 paired stock/C cases (4,160 executions): accepted and
invalid selectors, zero/one/two/high/maximum counts, four masks, optional final
callback and controlled mutations at bus-open, bus-close and shared-power calls.
It compares ordered policy state accesses, hardware/SDK call sequence and
arguments, final state, return words and preserved registers/stack/masks.
A deliberate mask snapshot before bus close fails: when that callback restores
mask one, stock skips shutdown while the variant performs it.

The normal report `build/sources-goal-r1-goodix-client-release/report.json`
compiles 569 R1 units without failures or duplicate strong symbols. Imports
remain 197 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-client-c-release-review.json) binds REA, source,
execution probe, negative control and the normal build by hash.

The C body is 196 bytes versus 154 native instruction bytes and is not
byte-qualified. The canonical source plan and G2 gates are unchanged.
Hardware/SDK calls are modeled; initialization/acquisition, concrete callback
targets, private frames/caller-clobbered registers/flags, concurrency, physical
power/reset behavior and complete source-only byte identity remain unverified.
The remaining SDK reset/interrupt hooks still require their own mapping proof.
