# R1 BAE8 connection-event adapter in C

`r1/src/application/board/native_bae8_connect.c` supplies
`r1_bae8_connection_event_plan_build` at stock application `0x7ccb4`. It adapts
the pinned Nordic SDK `ble_nus.c` `on_connect` skeleton to R1's two notification
channels, logging and connection callback. The Nordic license is retained.
The executable body is 198 bytes, ending at `0x7cd7a`; the previous 276-byte
frontier span included literals and the following string. REA's complete
276-byte window agrees with the locked application. The frontier now records
the code span separately from this wider evidence window.

The handler initializes its client output to null, looks up the connection,
and logs lookup failures without aborting. It reads the BC CCCD at service
offset 10 and EUS CCCD at offset 26 through SVC173. One mutable eight-byte
GATTS value descriptor is initialized once and reused for both reads, including
any length, offset or data-pointer changes returned by the first read.
Successful reads with a callback installed and notifications enabled set the
corresponding client byte to one. Disabled notifications leave existing bytes
unchanged. A remaining callback receives type zero even when neither read
enabled notifications; this differs from the narrower SDK skeleton behavior.

The new unit contains no inline assembly. It reuses the existing, unchanged
`r1_dfu_value_get` architectural SVC173 gateway. That gateway's historical
DFU name does not change its three-argument GATTS ABI.

## Frame and runtime evidence

The explicit C aggregate preserves these offsets in the manifest's current
Clang compilation. This is tested emitted behavior, not a guarantee across
arbitrary compilers or flags.

| Object | Offset from caller SP |
| --- | --- |
| Client output | -64 |
| GATTS value descriptor | -60 |
| 24-byte callback record | -52 |
| Two-byte CCCD buffer | -24 |

All direct provider entries retain a 64-byte thread frame. The actual
priority-2 table and C observer dispatch to the production connection handler
in 9,728 paired stock/C cases. Cases cover both controller results, notification
bits, null/non-null clients, lookup errors, basic and varying full-word log
modes, callback presence, both PRIMASK states, descriptor redirection and
mutations during providers/controller responses. Bounded hooks compare event,
service and client access order, widths and values. SVC arguments, descriptor
contents, callback bytes, state and restored registers/masks match. The second
SVC sees the first response's changed descriptor instead of reinitialized data.

Another 576 paired cases execute the actual C lookup, compiled SDK connection
index/validity and notification decoder, and existing SVC gateway. Flag-query
depth is 88 bytes on both paths. Checks include active/inactive links, both
read outcomes, redirected data pointers, notification values and preserved
preexisting flag bytes. Five negative controls reject descriptor reinitialization,
the wrong flag byte, wrong event type, larger frame and an uncleared record.

Lookup, log/mode providers, notification decoding, zero fill, application
callback and controller responses are modeled in the larger replay. In the
helper-chain replay only the flag query, log mode zero, zero fill, callback
and controller responses remain modeled. Supervisor exception frames and the
SVC return PC/LR differences between an inline instruction and gateway call
are excluded; parameter pointers and thread SP are checked. Void R0, internal
register values, APSR, private spills and timing are excluded. The application
event-route body, interrupt scheduling and physical BLE remain unvalidated.

## Build and qualification

`build/sources-goal-r1-bae8-connect-c/report.json` compiles all 594 units
(520 application, 74 bootloader). Both relocatable compositions pass without
failures or duplicate strong symbols. The other 593 objects are unchanged.
Application imports fall from 155 to 154; bootloader imports remain 34, with
no new imports. `make sources-check` passes with 398 R1 source files.

Qualification compiled the unit but selected no exact regions. The canonical
source plan is unchanged. A fresh hybrid application retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and totals of 4,269 source-built, 641,891 binary-pull-through and 248 resource
bytes. Complete C firmware and byte-identical source reconstruction remain
unproven. The subsequent [service configuration review](bae8-service-c-review.md)
supplies the initializer. The later [startup review](bae8-startup-c-review.md)
supplies transport startup. Application event routing remains unresolved;
resolving the observer's direct callees does not close it.

The [receipt](bae8-connect-c-review.json) records current object identity,
REA provenance, both replays, negative controls, qualification and audits.
Reproducible probes are under ignored `build/goal-r1-bae8-connect-c/`.
