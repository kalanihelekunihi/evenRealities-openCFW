# Heart-rate timing-result callback correlation

## Decision

The explicit Ghidra seed at `0x00049B60` is an independent R1 sensor-stream
callback. Its executable body is `0x00049B60..<0x00049BEE` (142 bytes,
SHA-256
`7f67cff79576a5a37f457e0e79ba43c092cc2db09afea26f56e2a7cee70717a5`).
The following log strings and literals extend its complete envelope across
`0x00049B60..<0x00049C64` (260 bytes, SHA-256
`fdbe3e53648384a8845fe85d6b17ebdcd2e0f0b95550c5e6eb2b741d773804c1`),
where the next native callback begins.

The function has no direct branch caller because the timing-start path stores
its Thumb pointer `0x00049B61` at literal address `0x00049B44` and registers it
with the sensor-stream framework. `r1_hr_timing_result_plan` is the compiled,
pure-C replacement for its R1-owned policy. The adjacent
`r1_hr_value_plausible` and `r1_hr_once_result_plan` APIs also make the already
classified `0x000499E0` and `0x000499F0` behavior concrete instead of leaving
their ownership names as documentation only.

## Record and publication contract

The callback consumes the provider's fixed three-byte record as heart rate,
confidence, and signal. The validity gate accepts the heart-rate byte in the
inclusive range 40 through 220. If that check and the recovered global health
publication gate both pass, it publishes internal event `6` with this exact
eight-byte payload:

| Offset | Encoding |
| ---: | --- |
| `0` | heart rate, UInt8 |
| `1...3` | zero |
| `4...7` | caller-supplied firmware clock, UInt32 little-endian |

Confidence and signal are retained for diagnostics but are not part of the
event. The clean planner accepts the clock and publication gate as inputs;
it never reads stock SRAM or a live clock and never dispatches an event.

## Lifecycle

Regardless of whether the value is invalid or publication is suppressed, the
stock callback unregisters its context from topic `"hr"` and clears the timing
stream handle. Its tail call to `0x00049D10` releases the timing timer when one
is present and clears that handle. The returned action plan preserves all four
intents. The one-shot wrapper shares validation and publication behavior but
does not request timer release.

The source API rejects null pointers and records whose length is not exactly
three, adding a bounded host-facing guard around the fixed-length stock
callback contract. Tests cover both inclusive range edges, both rejected
edges, enabled and suppressed publication, byte-exact clock encoding,
one-shot versus timing cleanup, and invalid arguments.

## Boundary

The generic sensor-stream framework remains in its separately reconstructed
module. Provider sampling, callback registration, firmware-clock production,
event-bus execution, timer release, and logging are not reimplemented by this
planner. No live optical control or callback injection surface is exposed.

## Verification

```sh
python3 tools/evidence/summarize_r1_hr_timing_result.py
```

The summarizer pins the recovered application hash, executable and envelope
hashes, zero direct-call set, registered Thumb pointer, all six policy
callsites, three diagnostic strings, publication layout, and cleanup tail.
