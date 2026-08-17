# GAP event policy correlation

## Decision

The explicit analysis seed at `0x00052B9C` is a real independent R1 GAP event
handler, not a literal-pool address inside the preceding BAE8 observer. It is
classified `r1_product_specific` / `clean_room_behavior_only`. The local
`r1_gap_event_plan_build` captures its connected, disconnected, PHY, and GATT
timeout policy as a pure plan. SoftDevice SVCs, Nordic connection state, link
context allocation, advertising, timers, logging, and live GAP dispatch remain
outside the clean-room function.

## Exact noncontiguous identity and registration

The handler occupies a 3,184-byte envelope through the next Ghidra function at
`0x0005380C`; that envelope hashes to
`1fe5a29f37f52ee7f0d7ea75ffb52dd65da44e37b3b64b2daffdc4efd6f62eac`.
Its actual control flow has two executable segments separated and followed by
ADR-addressed literal/diagnostic islands:

| Executable range | Bytes | SHA-256 |
| --- | ---: | --- |
| `0x00052B9C..<0x00052F9E` | 1,026 | `9aa721ab9b5f9adcd1478ffa3e2eb49b3e65a2a4ecbc3d219ef90610d5827453` |
| `0x00053278..<0x00053536` | 702 | `844baa6cfcf69cd6a4bc7b953152413158d6096d506a5b05f09d06c266caed62` |

The 1,728 executable bytes concatenate to SHA-256
`47e481cd2ccaf7721e760d015e4d9c503f819ba74ab1afcad277642647e4a282`.
There are no direct branch callers. Registration is the exact Thumb pointer
`0x00052B9D` at observer-table address `0x000C45C0`.

## Event routes

| BLE event | Route |
| ---: | --- |
| `0x10` | connected policy |
| `0x11` | disconnected policy |
| `0x21` | peer PHY-update request |
| `0x22` | PHY-update completion |
| `0x3B` | GATT client-timeout diagnostic |
| `0x56` | GATT server-timeout diagnostic |
| other | ignore |

### Connected

The stock handler cancels and reschedules its connection timeout for `0xF000`
ticks, caches the seven-byte peer record only for connection indices below
three, cancels both role timers, records the latest connection, and initializes
the first free slot in a three-entry link-context array. A provider error from
that slot initialization enters the existing fail-stop path; a full slot array
returns without inventing another context.

Factory marker `0x5A` additionally schedules the first role timer after
`0x7800` ticks. If the phone handle is invalid it requests the no-phone
advertising policy; otherwise it schedules the second role timer for the same
delay. Those named actions remain platform/provider operations.

### Disconnected

The handler cancels the connection and role timers, clears its connection
latch, releases the matching link slot, clears the bounded peer cache, and
queries the peripheral-link count. Role selection checks the glasses handle
before the phone handle and publishes role code `2`, `1`, or `0` while
forwarding the disconnect reason byte.

The glasses leg resets its transport and sensor/link state; the phone leg runs
the phone-disconnect/advertising policy. Both clear the matching cached handle.
The common tail validates the configured advertising TX-power SVC result,
accepting statuses zero and eight, starts advertising mode three, and schedules
the recovered retry callback after `0x66` ticks on start failure. The latest
connection handle is then invalidated.

### PHY and timeout events

For an event-`0x21` request on the glasses connection, peer RX/TX preferences
are swapped into local TX/RX order before tail-calling the already bounded PHY
provider adapter at `0x0004D2F4`; every other connection requests local
`1M/1M` (`1,1`). Event `0x22` reads status/TX/RX at bytes `8/9/10`: nonzero
status is failure, while successful TX or RX value four is classified coded.
The two GATT timeout events only produce their distinct diagnostics.

## Clean-room model

`r1_gap_event_plan_build` accepts explicit event bytes, cached role handles,
factory state, link-slot/provider results, and advertising outcomes. It emits
only bounded action intent and fixed parameters. It never accepts a live BLE
event pointer, calls a recovered address, allocates link state, issues an SVC,
starts advertising, schedules a timer, or logs. Host tests cover every event
route and the connected/disconnected/PHY branch points, including slot-full,
provider-error, factory, all three roles, accepted TX-power statuses, retry,
coded/non-coded/failure, and unknown-event behavior.

## Verification

```sh
python3 tools/evidence/summarize_r1_gap_event_policy.py
```

The summarizer pins the full envelope and both executable hashes, observer
registration, timer/link/advertising/PHY provider callsites, event routes, and
representative exact diagnostics. The adjacent BAE8 raw observer and Nordic
handlers retain their independent ownership rows.
