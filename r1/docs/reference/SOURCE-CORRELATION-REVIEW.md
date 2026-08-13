# Application source-correlation review

## Purpose

the raw BSim correlation CSV (regenerable; see [`bsim/APPLICATION-SOURCE-CORRELATION.md`](bsim/APPLICATION-SOURCE-CORRELATION.md)) is a ranking aid, not an
ownership verdict. Its normalized comparison is valuable for locating candidates, but exact scores
on tiny thunks can arise when unrelated functions share the same register shuffle or tail-call
shape. Provider admission still requires complete function semantics, call context, constants, and
an attributable source body.

This review records rejected top-ranked candidates so regeneration or later research does not turn
a similarity score into a false vendor attribution. Rejected entries remain `unclassified` and
`investigate_before_implementing` in `FUNCTION-OWNERSHIP.csv`.

## Rejected exact-score candidates

| R1 extent | Raw top match | Review result | Function-local evidence |
| --- | --- | --- | --- |
| `0x0002907C..<0x0002908E` | `app_error_fault_handler` | Reject | The body saves and forwards stacked arguments to `0x00037890`. Its sole recovered caller at `0x000968C4` supplies seven algorithm parameters and tests the return value. It is an ABI argument-forwarding shim, not Nordic's fail-stop/reset fault handler. |
| `0x00035412..<0x0003541A` | `PkaInitAndMutexLock` | Reject | The body moves its second argument, forces the middle argument to `1`, and tail-calls `0x0003540C`. The callee belongs to the adjacent YHM2710 control cluster and ultimately dispatches through the product/provider state at `0x000507CC`; no CryptoCell PKA or mutex semantics are present. |
| `0x00071704..<0x0007170A` | `nrf_atomic_flag_set_fetch` | Reject | The body loads the constant length `0x5A` and tail-calls the recovered zero-fill helper at `0x000277AA`. It is a fixed-size buffer clearer, not an exclusive-load/store atomic primitive. |
| `0x00071B24..<0x00071B2A` | `nrf_atomic_flag_set_fetch` | Reject | The body loads the constant length `0x48` and tail-calls the same zero-fill helper. Callers use it as a structure reset. |
| `0x0004E650..<0x0004E65E` | `app_error_fault_handler` | Reject | The wrapper places `200` in the fifth argument slot, selects mode `1`, and calls the product queue/service function at `0x0003E7A8`. |
| `0x0004E65E..<0x0004E66C` | `app_error_fault_handler` | Reject | The sibling wrapper places `100` in the fifth argument slot, selects mode `0`, and calls `0x0003E7A8`. Neither wrapper has Nordic fault/reset behavior. |

The exact two- and four-byte matches against `_stack_init` and `wmap` are also non-actionable.
Returns, empty veneers, and single tail branches do not contain enough distinguishing information
for source attribution.

## Admission rule for later passes

A correlation candidate may cross the ownership gate only when all of the following hold:

1. The complete R1 function extent is known and the comparison covers the meaningful body.
2. Constants, branches, state updates, error behavior, and callable ABI agree with a pinned source.
3. Direct callers/callees and surrounding subsystem evidence do not contradict that source.
4. The provider version and license are already admitted, or the result is recorded as a disabled
   licensed-provider boundary.
5. A short function is supported by a distinctive hardware register, source-only discriminator,
   or larger call-graph closure; byte identity of a generic thunk alone is insufficient.

This review does not classify the rejected bodies as R1-owned. It preserves the stricter conclusion:
their origin remains unknown, so local reimplementation is still blocked.
