# R1 SpO2 synchronization-flush correlation

## Disposition

Two formerly unclassified functions / 578 executable bytes are admitted as R1-specific SpO2
day-packet reset, serialization, flush, and acknowledgement-context behavior. They are
`r1_product_specific` / `clean_room_behavior_only`; no third-party implementation has been
identified, and neither function calculates oxygen saturation or processes sensor signals.

This closes the packet-emission seam adjacent to the already admitted scalar-health offline
queues and automatic SpO2 history-sync orchestrator. It does not admit the unresolved
time/calendar provider, topic selector, transport sender, or any Goodix algorithm.

## Exact closure

| Entry | Bytes | SHA-256 | Role |
| --- | ---: | --- | --- |
| `0x00043C80` | 32 | `3725b1988300ebb4258420db5e99c5cddc5674b826476027653d69ec00437e0b` | reset the 148-byte SpO2 day builder while preserving timezone and transport configuration |
| `0x000442F4` | 546 | `19780f7fc4d8f489e8776cfacd080a445258c250845460e305942bfa41f4ccc2` | reject future packets, assemble the sparse 24-hour packet, create optional ACK context, invoke the abstract sender, and reset the builder |

The reset helper has five direct branch callsites. The flush routine also has five, from the SpO2
RAM/flash merge and history paths. Already product-routed offline merge `0x000448B0` and history
sync `0x0008CD60` are among those callers. The summarizer freezes each complete body and its
direct caller-set digest, so a shifted extent or changed callgraph fails verification.

## Packet behavior

The flush returns immediately for a null or empty builder. It samples the abstract firmware
clock and rejects a builder whose day timestamp or newest-record timestamp lies in the future,
then resets the builder. Otherwise it allocates exactly `12 + count * 4` bytes and writes:

- byte 0: the number of present hourly slots;
- bytes 1-2: the builder's two-byte timezone field;
- bytes 3-6: the day timestamp;
- bytes 7-11: the cached latest-SpO2 word and its one-byte companion, or five zero bytes when the
  daily cache accessor at `0x0005BAEC` has no record; and
- byte 12 onward: one four-byte value for each present slot among the 24 bounded slots.

When acknowledgement tracking is configured, the routine allocates an eight-byte context
containing the builder's mode byte and newest-record timestamp. It obtains the abstract topic,
invokes the unresolved packet sender, frees the packet through authenticated FreeRTOS
`vPortFree`, and resets the builder after either send outcome. Initial packet-allocation failure
returns without clearing queued state; acknowledgement-context allocation failure is logged and
the send proceeds without that context.

The 32-byte reset helper preserves the two-byte timezone, acknowledgement callback/context, and
mode fields while clearing the 148-byte builder. A clean implementation can use caller-owned
buffers and an injected emission callback instead of recreating the stock heap or transport.

## Provider and safety exclusions

Local code may implement the bounded packet/reset policy, but must not recreate:

- authenticated FreeRTOS `pvPortMalloc` / `vPortFree`;
- the unresolved time/calendar backend at `0x0008ADA4`;
- the unresolved topic accessor at `0x0008ACFC` or packet sender at `0x00083792`;
- Nordic's separately source-routed logging frontend and the R1 structured-log cache; or
- Goodix signal processing, daily-value generation, or biometric algorithms.

The summarizer is static, reads no private history, and exposes no live sender.

## Reproduce

```sh
python3 scripts/firmware/summarize_r1_spo2_sync_flush.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```
