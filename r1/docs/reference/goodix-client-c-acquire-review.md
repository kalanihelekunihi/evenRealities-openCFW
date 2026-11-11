# Goodix reference-counted acquire reconstructed in C

REA confirms previously unlisted stock entry `0x50b00` is the acquire partner
of `0x50be0`. Its C implementation shares the existing mode table, eight-word
counter storage, active mask and callback word in `stock_client_release.c`.
No second state owner or new unresolved boundary is introduced.

Selectors 1/2/3/4/5/7 use matching counter slots; selector 6 shares slot 2.
Selectors 8/9 use special mode `0x2000`; zero or selectors at least ten reject
without state accesses. Count increments wrap unsigned. New count greater than
one returns early; both zero and one continue startup. Maximum-count wrap to
zero therefore enters initialization, as stock does.

Normal first startup reads whether the active mask is empty before callbacks.
Cold initialization acquires shared power, prepares transport, raises reset,
opens IRQ, opens the bus, switches configuration zero and closes the bus.
The active mask is then freshly read and ORed with the mode. All normal starts
open the bus and start sampling. Only a cold start configures watermark 25 and
reloads/calls the optional callback with zero. A final bus close completes it.
Callback mutations cannot be replaced with an earlier mask/callback snapshot.

Forced startup uses a distinct sequence: shared power, reset high, transport,
bus open, delay 10 ms, demo initialization, IRQ open, configuration two, sampling
mode `0x2000`, watermark five and bus close. It does not increment the policy
counter, alter the mask itself or call the policy callback. External-call
state changes remain observable. External declarations use the actual SDK
parameter/return widths, including the demo initializer's int return.

The execution probe passes 2,080 paired stock/C cases (4,160 executions), with
invalid/special/normal selectors, counts including maximum wrap, four masks,
optional callbacks and controlled mutations at bus close, shared-power acquire
and watermark configuration. It compares ordered policy state accesses,
external call sequence/arguments, final state and preserved registers/stack/masks.
All 2,080 release regressions pass against the same current object. A deliberate
variant requiring count exactly one fails on maximum-count wrap to zero: stock
initializes while the variant skips startup.

The normal report `build/sources-goal-r1-goodix-client-acquire-verified/report.json`
compiles all 569 R1 units without failures or duplicate strong symbols. Imports
remain 197 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-client-c-acquire-review.json) binds REA, source,
execution probes, negative control and normal build by hash.

The C acquire body is 238 bytes versus 212 native instruction bytes and is not
byte-qualified. The canonical source plan and G2 gates are unchanged. Hardware
and SDK calls are modeled; initial startup contents/placement, concrete callback
targets, private frames/caller-clobbered registers/flags, concurrency, physical
power/reset/timing and complete source-only byte identity remain unverified.
