# advStart and touchSwitch handler correlation

## Outcome

Two system-table handlers that Ghidra seeded but omitted from the canonical function inventory are
now represented by strict, side-effect-free C plans:

| Recovered extent | Bytes | SHA-256 | Clean plan |
| --- | ---: | --- | --- |
| `0x00083D04..<0x00083D5A` | 86 | `435f50237fe6a1501c14ba62cab220e522d4820e706a6302b721ffcdb3dbfb95` | `r1_connection_control_adv_start_handler_plan_decode` |
| `0x00084874..<0x0008492C` | 184 | `48de556b7d5d748c313316c773fd93f6ae51ac9075ed8d33079c390c8fbc02df` | `r1_touch_switch_handler_plan_decode` |

Both bodies have independent prologues and complete return paths. The advStart body ends before the
independent device-info handler at `0x00083D5C`; touchSwitch ends with its close-source return at
`0x0008492A`. The system table registers advStart identifier `0x000A` at `0x0009A50C` as raw bytes
`0a000000053d0800` and touchSwitch identifier `0x0007` at `0x0009A4F4` as raw bytes
`0700000075480800`.

## advStart boundary

The legitimate advStart payload is exactly 12 bytes: two independent six-byte target addresses.
On the successful production route, the handler sends an empty success response on the incoming
request session before allocating and queuing event `0x200`. The event uses the current EUS session,
which can differ from the incoming session. Queue or allocation failure cannot change the earlier
response.

Stock length arithmetic also accepts malformed declared lengths `0...11` through unsigned wrap and
would then read beyond the declared payload. That behavior is evidence only. The clean plan accepts
exactly 12 caller-supplied payload bytes, copies both targets, and records the distinct response and
event sessions. It performs no response send, allocation, queue operation, target persistence,
disconnect, advertising, or BLE access. The already-tested
`r1_connection_control_plan_adv_start` remains the separate event-consumer policy.

## touchSwitch boundary

After locating a non-header payload, production sends an empty success response before inspecting
two bytes. Payload byte 0 is a selector and byte 1 is the switch value:

| Selector | Recovered behavior |
| ---: | --- |
| `1` | phone diagnostic only; no touch-source mutation |
| `2` | nonzero opens touch source 0; zero closes touch source 0 |
| other | acknowledged no-op |

The clean plan requires exactly two backing bytes. It reports the response intent and one of
`PHONE_DIAGNOSTIC`, `OPEN_GLASSES_SOURCE`, `CLOSE_GLASSES_SOURCE`, or `NONE`; it never logs or calls
the recovered source manager. The authorized portable dispatcher now uses this exact selector/value
shape. It no longer interprets a one-byte selector as an enable boolean. Only the glasses selector
changes the portable touch-enable policy, whose board adapters retain their existing identity,
wear/factory lease, shared-power, and owned-hardware gates.

## Tests and safety

Host tests cover null arguments, short and trailing payload rejection, both target copies, distinct
incoming/current sessions, event `0x200`, both glasses actions, the phone diagnostic-only selector,
unknown-selector no-op behavior, and rejection of the former ambiguous one-byte touch shape. No
firmware bytes, recovered pointers, BLE sender, RTOS object, hardware driver, or opaque executable
element enters the build through these plans.
