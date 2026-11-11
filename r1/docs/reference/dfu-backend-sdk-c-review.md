# DFU backend through Nordic typed SVC APIs

`r1/src/application/runtime/native_dfu_backend.c` replaces its three handwritten
SVC wrappers with calls to the pinned Nordic SDK APIs: `sd_ble_gatts_hvx`,
`sd_power_gpregret_clr` and `sd_power_gpregret_set`. The local
`SVCALL_AS_NORMAL_FUNCTION` override is removed, allowing the SDK declarations
to own service numbers and the architectural call ABI. The existing forwarding
symbols remain ordinary C functions. SDK-generated SVC/return instructions are
still required; this does not remove the architecture boundary.

Compile-time assertions bind the recovered DFU context to connection handle at
+4, value handle at +6 and event handler at +20. They also bind the 16-byte HVX
parameter record to its handle, type, offset, length pointer and data pointer.
The known caller reads a 16-bit connection handle; the C forwarding call uses
the SDK's uint16_t parameter type. Arbitrary high-bit raw arguments outside that
caller contract are not covered.

The response frame remains protected by its existing adapter. Unwritten bytes,
including the high halfword of the length word and the byte beyond the three
payload bytes, retain caller history. The actual length pointer aliases that
frame. HVX success with a returned length other than three still returns 12;
nonzero service errors pass through unchanged. Finalization clears GPREGRET0
with mask UINT32_MAX, sets it to 0xb1 only after success, then calls the live
DFU event handler and requests shutdown. A failed service stops that sequence.

Fresh REA code windows for 0x522d8 and 0x52050 match the preserved application.
The final normal product object passes **4550 stock/previous/new cases (13650
executions)**: 4250 response cases and 300 finalization cases. Independent
oracles check service numbers 174/61/60, arguments, statuses, payload bytes,
parameter/length pointer aliases, retained frame bytes, all selected returned
lengths, truncation of opcode/response bytes, error gates, event-handler
replacement, shutdown order, context bytes, SP, saved registers and interrupt
masks. SDK SVC instructions execute; service effects and callbacks are modeled.

The existing shared-state fixture also passes **1728 paired sequences**, linking
the actual SDK owner and updated backend. It confirms one 12-byte asynchronous
state object and shared SVCI3/callback state across initialization, name dispatch
and invalid-state event handling. Four compiled defect controls are detected:
incorrect HVX service, incorrect clear service, incorrect retained mask and
discarded clear status. The final normal implementation is rerun after controls.

All **801 units (719 application, 82 bootloader)** compile without failures or
duplicate strong symbols. Imports remain 95 application and 22 bootloader linker
metadata symbols; strict GNU bootloader linking passes. All 798 other
nongenerated prior object hashes are unchanged. Generated boot vectors/crypto
retain identical allocated bytes/relocations, and all nine other backend function
bodies remain unchanged. The R1 manifest check passes; the global check retains
the unrelated unlisted G2 resident-ROM assembly file. Source-plan selections
are unchanged. [The receipt](dfu-backend-sdk-c-review.json) records input/header,
object and probe hashes.

Private helper frames, live temporary registers, incidental caller-clobbered
outputs, APSR and complete exception frames are excluded. Shared-state tests
model vector selection, SVCI resolution and callbacks. BLE notification delivery,
physical GPREGRET mutation, actual shutdown/DFU transfer, asynchronous behavior
and complete application final linking remain unverified.

The newer [authorization SDK call review](dfu-auth-sdk-c-review.md) links this
backend into authorization, response, HVC and finalizer comparisons.
