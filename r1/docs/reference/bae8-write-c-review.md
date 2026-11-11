# R1 BAE8 write-event adapter in C

`r1/src/application/board/native_bae8_write.c` supplies
`r1_bae8_write_event_plan_build`, stock application `0x7cf4c` (258 code bytes).
It adapts the pinned Nordic SDK `ble_nus.c` `on_write` skeleton to the observed
R1 four-characteristic layout, event types and logging. The license is retained.
The existing observer dispatches to this one C implementation.

Context lookup errors are logged without aborting processing. A BC CCCD write
matches service offset 10 with length exactly two and updates client byte zero;
notification enabled/disabled emits type 6/7. The EUS CCCD at offset 26 updates
client byte one and emits 8/9. BC/EUS payload handles at offsets 14/30 emit
type 2/3, retaining the event payload pointer at event offset 18 and the full
16-bit length from offset 16. Null contexts suppress notification transitions
but do not suppress payload callbacks. Handle alias precedence, mutable client
reloads and callback reloads follow stock control flow.

## Frame and runtime evidence

The native context-output slot is at caller SP minus 32, and the 24-byte
callback record is at caller SP minus 56, with a 56-byte provider frame.
Ordinary C locals compiled into different addresses. The accepted version
uses an explicit aggregate containing the record, volatile client output and
unread private padding, aligned to eight bytes. The current manifest's Clang
build preserves both addresses and the frame without inline assembly. This
is verified for the current compilation, not guaranteed for every compiler.
Static assertions protect record offsets and aggregate size; runtime replay
checks the emitted addresses.

The production object is reached through the actual priority-2 table and C
observer in 13,360 paired stock/C cases. These cover notification and payload
writes, basic log-mode combinations and varying full-word modes, failed lookup,
null contexts, lengths 0/1/2/3/65535, handle aliases, callback presence, both
PRIMASK states and mutations during provider calls. Bounded memory hooks
compare event, service and client access widths, order and values. Callback
record bytes, provider arguments/results, state, restored SP, callee-saved
registers and interrupt masks match.

Another 480 paired cases execute the actual C lookup plus compiled SDK
connection index/validity and notification decoder, against their stock
bodies. Both escaping pointers remain fixed, and the flag-query provider
depth is 80 bytes on both paths. Five negative controls reject a smaller frame,
widened CCCD length check, cached client pointer after notification decoding,
wrong BC event type and uncleared record. The record retains its earlier
client snapshot while the notification store reloads the output pointer.

Lookup, mode/log providers, notification decoding, zero fill and application
callback are modeled in the larger replay. In the helper-chain replay only
the flag query, log mode zero, zero fill and callback remain modeled. Void R0,
internal nonargument registers, live non-tail callee registers, APSR, private
spills and timing are excluded. The actual application event-route body,
interrupt scheduling and physical BLE writes remain unvalidated.

## Build and qualification

`build/sources-goal-r1-bae8-write-c-final/report.json` compiles all 593 units
(519 application, 74 bootloader). Both relocatable compositions pass without
failures or duplicate strong symbols. The previous 592 objects are unchanged.
Application imports fall from 156 to 155; bootloader imports remain 34, with
no new imports. `make sources-check` passes with 397 R1 source files.

Qualification compiled the new unit but selected no exact regions. The
canonical source plan is unchanged. The fresh hybrid application retains
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and totals of 4,269 source-built, 641,891 binary-pull-through and 248 resource
bytes. Complete C firmware and byte-identical source reconstruction remain
unproven. The subsequent [connection review](bae8-connect-c-review.md) supplies
the connection-event handler; service configuration and event routing remain.

REA's handler/literal/string window agrees with the locked application. The
[receipt](bae8-write-c-review.json) records provenance, current object identity,
both replays, negative controls, qualification and build audits. The SDK
notification helper's application frontier now references its current tested
object; no byte-identity claim was added. Reproducible probes are under ignored
`build/goal-r1-bae8-write-c/`.
