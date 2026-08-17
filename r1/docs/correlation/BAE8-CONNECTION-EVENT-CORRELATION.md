# BAE8 connection-event and CCCD correlation

## Decision

The Ghidra-omitted closure at `0x0007CCB4..<0x0007CDC8` is the R1-specific
connection handler for the custom four-characteristic BAE8 GATT service. It is
classified `r1_product_specific` / `clean_room_behavior_only`. The local
`r1_bae8_connection_event_plan_build` reproduces only its observable decision
policy; Nordic link-context management, SoftDevice GATT value access,
`ble_srv_is_notification_enabled`, logging, and live callback dispatch remain
provider/platform operations.

## Exact identity and route

| Recovered range | Bytes | SHA-256 |
| --- | ---: | --- |
| `0x0007CCB4..<0x0007CDC8` | 276 | `e72b8ea7bb55915ba8783ea67e76a3d0d747eb32f808f66e48da2a0a2ba3385a` |

The first 198 bytes, through `0x0007CD7A`, are executable and hash to
`869bf2a4799c3d53a701556c7fddcb6f48df477405a7a0c1e323d47f0bb94083`.
The remainder is the aligned literal and diagnostic-string pool ending at the
next function, `0x0007CDC8`. The sole caller is the `B.W` at `0x00052B58` in
`r1_bae8_raw_observer`; observer event ID `0x0010` selects this tail call.

## Recovered service layout and behavior

The handler receives the BAE8 service object and connected BLE event. It uses
the connection handle at event offset `+4` and the following service fields:

| Field | Offset |
| --- | ---: |
| link-context manager | `0x28` |
| channel-1 TX CCCD handle | `0x0A` |
| channel-2 TX CCCD handle | `0x1A` |
| service event callback | `0x2C` |

It initializes the returned link-context pointer to null and calls the Nordic
link-context lookup at `0x000514E0`. Failure produces the exact diagnostic
`Link context for 0x%02X connection handle could not be fetched.` but does not
stop processing.

For each TX CCCD, the handler builds a two-byte, offset-zero value descriptor
and issues SoftDevice SVC `0xAD` at `0x0007CD1E` and `0x0007CD3A`. A successful
read is tested with Nordic `ble_srv_is_notification_enabled` at `0x0007CD28`
or `0x0007CD46`. The corresponding link-context byte at offset zero or one is
set to one only when all four conditions hold: the read succeeded, notification
bit `0x0001` is set, a callback is installed, and link context exists. Disabled
or unreadable CCCDs are not actively cleared by this handler.

If the callback exists, a zeroed 24-byte event record is emitted after both
reads. Event type is zero; the record carries the service pointer, connection
handle, and link-context pointer. A null link-context pointer is intentionally
allowed after lookup failure. If no callback exists, both CCCD reads still
occur, but neither context flag nor event dispatch is requested.

The pure C planner expresses each provider read, conditional one-way flag
update, failure diagnostic, and callback decision without accepting service
pointers or invoking BLE. Host tests cover enabled notification values,
indication-only value `0x0002`, read failure, missing context, missing callback,
the fixed event type, and the 24-byte record size.

## Verification

```sh
python3 tools/evidence/summarize_r1_bae8_connection_event.py
```

The summarizer pins the complete closure and executable hashes, sole observer
tail call, both SVC sites, both Nordic CCCD-helper calls, service offsets,
literal pool, and exact diagnostics. No neighboring function or provider body
changes ownership by association.
