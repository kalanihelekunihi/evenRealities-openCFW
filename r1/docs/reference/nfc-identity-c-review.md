# NFC identity probe reconstructed in C

This historical review includes incidental register/frame behavior. The current
[assembly-free NFC implementation](nfc-pure-c-review.md) preserves the typed
byte-output C contract and documents the intentionally excluded private state.

`st25/native_identity.c` supplies the missing ST25 identity adapter at `0x77c50`
and board probe at `0x503b4`. The inner adapter clears only the low byte of its
saved incoming R3 word, registers the existing provider, calls
`ST25DVxxKC_ReadID` on the existing object at `0x20016b08`, logs as enabled, and
returns the current ID byte. Registration and ReadID status words do not stop
this sequence or replace that byte. The ReadID prototype matches the export
in the pinned provider C file; that export is absent from its public header.

The outer probe acquires the existing I2C5/NFC resource, calls `nrf_delay_ms(50)`,
executes the identity adapter, releases the resource, then logs and returns the
ID. It preserves the acquired ID across release and logging callbacks. Both
functions retain separate mode queries for the bit-0/bit-2 ring conditions
and bit-1 SDK condition, including short-circuit behavior. Inner logging and
return reload the byte so callback writes remain visible. Stock log strings,
including the outer carriage return, and both logging tags are preserved.

The actual C inner/outer chain passes 15,872 paired stock/C cases. These cover
all 256 ID bytes, registration/ReadID error statuses, untouched/byte/full-word
read effects, all three-mode combinations plus changing six-mode patterns,
and full-word scratch mutations during registration, mode queries and logging.
Tests compare ordered provider/logging calls, byte/word effects, live R4–R11,
final R0, standalone restored R3, SP and interrupt masks. Wrong delay, full-word
clearing, Boolean ID conversion and collapsed mode-query variants are rejected.

The outer frame matches stock at eight bytes. The inner C frame is 16 bytes
versus native eight; its buffer location is normalized in the fixture, while
contents and callback-visible effects are compared. Neither routine qualifies
byte-for-byte, and no exact region is selected. Private return words, flags and
other caller-clobbered registers are excluded. Electrical response, actual delay,
arbitrary aliases/faults/concurrency and complete source-only rebuilding remain
unproven; all external providers are modeled.

All 583 R1 units compile. All 582 prior objects and 164/34 import sets remain
unchanged. No duplicate ST25 object or provider is added. The canonical hybrid
still contains 4,155 source-built bytes, 642,005 fallback bytes and 248 resource
bytes and matches the locked application SHA-256. Probes, REA readbacks and
audit are under `build/goal-r1-nfc-identity-c`; durable results are in the
adjacent JSON.
