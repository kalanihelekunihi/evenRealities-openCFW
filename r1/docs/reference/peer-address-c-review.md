# C peer-address, disconnect, power and report closure

The eight lower dependencies exposed by the BLE consumer now have C providers.
This closure includes the address validator and checked disconnect helper they
need, and removes the common response-header helper's scratch-register assembly.
The normal build compiles 845 units (763 application, 82 bootloader), with
71 application imports and 22 bootloader linker imports: eight close, none appear.

The new 21-byte connection-slot cache is separate from the existing GAP controller/
target records. Its native extent is inside the authenticated zero region and
between the two advertising contexts. Target records and battery runtime state
reuse their existing owners. No duplicate cache of those fields is introduced.

Lookup preserves index0..2 and null-output guards and copies bytes1..6 of each
seven-byte slot. Target validity rejects zero/ff addresses. Matching keeps the
captured validity decisions but reloads target bytes after diagnostics; missing
targets or unavailable slots preserve the native permissive result. Target
updates keep flag bit0, add0x14, persist the original nullable pointers, and log
live cached bytes after persistence. Deferred disconnect rechecks both target
policy and connected state, then uses the typed S140 reason0x13 interface.
Transmit power uses connection role/level6 with the original error continuation.
Charge refresh, ear-worn and op8 records preserve their order and initialized
payloads.

The [review receipt](peer-address-c-review.json) records 5,494 direct stock/C
comparisons, 4,641 through the actual C consumer and 144 through the encoder,
prepared FIFO, consumer, new peer/power/report helpers and SDK parameter gates.
Twenty compiled defects are rejected, followed by full unmodified verification.
The probes cover every validity/flag byte, aliasing, cached/live state, repeated
connection checks, SDK statuses, emitted records and scalar response results.
Standard memory/comparison code and the SDK SVC instructions execute; lower
service results, storage, logs, scheduler and transport backends are models.

The common response helper now uses ordinary C outputs. Current statically
resolved C callers consume R0; wrappers with saved scratch-word behavior restore
their own values. Direct header tests and the op8 consumer path verify public
packet/result behavior. Native incidental r2/r3 results and hypothetical external
or indirect consumers remain outside that contract. Existing charge predicates
and other register-dependent status workers are unchanged.

All 831 other prior nongenerated objects remain identical. Existing transmit-power
sections retain their bytes; only its added helper sections and the common
response function change. Correcting the consumer's op8 return declaration also
retains identical consumer object bytes. The R1 manifest check passes. The global
check still reports the pre-existing G2 `resident_rom_thumb_set.S` entry.

The composite probe preloads connection slots: the separate GAP event writer
remains open and connected-event cache population is not proven. Internal helper
inlining is allowed; mutations occur at modeled backend/SDK boundaries. Final
linking, runtime placement, physical timing and device boot remain unverified.
Byte identity and a paid compiler are not required.
