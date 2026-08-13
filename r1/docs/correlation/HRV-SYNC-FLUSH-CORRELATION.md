# R1 HRV synchronization-flush correlation

## Disposition

Two formerly unclassified functions / 616 executable bytes are admitted as R1-specific HRV
day-packet reset, serialization, flush, and acknowledgement-context behavior. They are
`r1_product_specific` / `clean_room_behavior_only`; no third-party implementation has been
identified, and no biometric calculation occurs in either function.

This supplements the already admitted scalar-health offline queues and automatic HRV history-sync
orchestrator. It does not admit the unresolved time/calendar provider, topic selector, packet
transport sender, or any Goodix/GoMore algorithm.

## Exact closure

| Entry | Bytes | Role |
| --- | ---: | --- |
| `0x00040964` | 32 | reset the 220-byte HRV day builder while preserving timezone, callback, and mode configuration |
| `0x0004101C` | 584 | reject future packets, assemble the sparse 24-hour packet, create optional ACK context, invoke the abstract sender, and reset the builder |

The two-function closure totals 616 bytes. `summarize_r1_hrv_sync_flush.py` freezes both complete
body hashes and their caller sets. The reset helper has five callers, all within the same HRV
RAM/flash merge, flush, offline merge, and history-sync family. The flush routine has five calls
from those same family paths, including already product-routed HRV offline merge `0x00041638` and
history sync `0x0008C750`.

## Packet behavior

The flush routine returns immediately for an empty builder. It samples the abstract firmware
clock and drops a builder whose day or newest-record timestamp lies in the future. Otherwise it
allocates a packet, writes the slot count, signed timezone offset, day timestamp, and the six-byte
latest HRV point from the daily cache (or zeros when unavailable). It then walks all 24 hour slots
and copies each present slot as seven bytes: a four-byte field, a two-byte field, and one byte.

The serialized size is therefore `13 + count * 7`. When acknowledgement tracking is configured,
the routine allocates an eight-byte context containing the builder's mode byte and newest-record
timestamp. It obtains the abstract topic, invokes the unresolved packet sender, frees the packet
through authenticated FreeRTOS `vPortFree`, and resets the builder after either send outcome.

The 32-byte reset helper preserves only the signed timezone, acknowledgement callback/context,
and mode fields while clearing the packet state. A clean implementation uses caller-owned buffers
and the existing emission callback, so it need not reproduce stock heap allocation or transport.

## Provider and safety exclusions

Local code may implement the bounded packet/reset policy, but must not recreate:

- authenticated FreeRTOS `pvPortMalloc` / `vPortFree`;
- the unresolved time/calendar backend at `0x0008ADA4`;
- the unresolved topic accessor at `0x0008ACFC` or packet sender at `0x0008362C`;
- Nordic's separately source-routed logging frontend and the R1 structured-log cache; or
- Goodix/GoMore signal processing, daily-value generation, or biometric algorithms.

The summarizer is static, reads no private history, and exposes no live sender.

## Reproduce

```sh
python3 scripts/firmware/summarize_r1_hrv_sync_flush.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```
