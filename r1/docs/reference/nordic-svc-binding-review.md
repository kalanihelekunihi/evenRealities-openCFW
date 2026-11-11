# R1 radio-address gateway supplied by the Nordic SDK

The handwritten `svc; bx lr` wrapper was removed from product advertising
configuration. A separate C translation unit includes pinned S140 `ble_gap.h`
and aliases its SDK-generated `sd_ble_gap_addr_get` implementation to the
existing `r1_advertising_controller_address_get` name. Clang emits one global
four-byte body, with no forwarding frame or duplicate gateway. The required
assembly now comes from the pinned SDK's `nrf_svc.h::SVCALL` macro; this is
SDK reuse, not a claim of portable-C hardware exception generation.

The emitted bytes remain `6d df 70 47`, exactly matching the previous local
gateway. Every other allocated advertising section and normalized relocation
is unchanged. REA observes `svc 0x6d` at `0x48A52` inside the locked 148-byte
advertising-configuration function. Stock inlines that SVC; it does not
establish a separate native four-byte wrapper at that location.

All 36 old-versus-SDK gateway execution comparisons pass, checking exception
number, SVC immediate, argument pointer, SP/LR, return status, r1–r7 and
controlled output storage. Cases include aligned/unaligned pointers,
untouched/written output, three return words and two register seeds. The
exception handler is a mock; resident SoftDevice implementation, real error
policies, radio behavior and hardware exception entry/return remain untested.

All 562 R1 units compile: 488 application and 74 bootloader units. Both
compositions pass with no duplicate strong symbols; undefined sets remain
241 application and 34 bootloader imports. No source-plan selection, accepted
pseudocode receipt or workflow gate changed. The new source unit owns the
SDK binding previously embedded as product assembly; it is not another body.

[nordic-svc-binding-review.json](nordic-svc-binding-review.json) binds SDK
header hashes, source/report identities, the section/relocation comparison,
REA observations and controlled SVC cases. Probes remain under ignored
`build/goal-r1-sdk-svc/`. Complete source linking, whole-image byte identity
and physical hardware operation remain open.
