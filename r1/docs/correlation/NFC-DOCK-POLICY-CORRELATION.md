# NFC dock mailbox and field-control policy correlation

## Decision

Four R1 adapter functions / 620 executable bytes are byte-pinned as product policy around
the ST25DVxxKC provider. They contain R1 dock-command framing, heartbeat state, rectifier-ADC
delay selection, and a product field-seen flag. They do not implement ST register access or
mailbox transport and are eligible for a clean-room behavioral implementation.

The evidence gate is
`../../tools/evidence/summarize_r1_nfc_dock_policy.py`.
It checks the recovered application SHA-256, every function body, direct caller set, the dock
state pointer, the shared field-seen state pointer, and the delayed-callback pointer.

| Entry | Size | Clean-room role | Body SHA-256 |
| --- | ---: | --- | --- |
| `0x000772A8..<0x00077336` | 142 | build and submit the R1 23-byte dock-advertisement command | `831d81b9484b6ed2e7551144aa1a831fb9cea0bec4afe5535e0cc7e1cd74ffa3` |
| `0x00077430..<0x00077602` | 466 | dock identity heartbeat, delay selection, and field-control dispatch | `ae5760b9a6ac03ac46642f7e19b90b11b0e630c406e443902ce1cb31c99a30e1` |
| `0x00096A48..<0x00096A4E` | 6 | field-seen getter | `8292370a09b6beb685b201c7106057995b3213e3f1681af6649f9a5c52de0d2d` |
| `0x00096A54..<0x00096A5A` | 6 | field-seen setter | `0594a3e6604c4c62a70819ee5094ceab26fb2eb8fbb5280fd4b92fff602100ce` |

The 466-byte dispatcher has one direct caller at `0x00077C44`, inside the already admitted
bounded ST25DVxxKC mailbox-receive adapter. Its advertisement helper has one direct callsite
at `0x000774F0`. The field-seen setter is called at `0x000774D2`; the getter is consumed by
the public product-protocol query at `0x000628BA`.

## Recovered behavior

A dock identity record begins with bytes `01 02 03 04` and is at least nine bytes long.
Two following big-endian 16-bit values are rendered using the stock
`%d.%d.%d.%04d` shape into an 11-byte buffer, and byte 8 is retained as the dock accessory
value. Every accepted identity record increments an 8-bit heartbeat counter and sets the
field-seen flag.

Only dynamic mailbox-control byte `0x81` permits a reply. The first permitted reply mutates
bytes 1..3 of the existing 23-byte product packet to `55 03 <marker>`, transmits it, and sets
the marker to `0xAA`. Later replies preserve the packet and synchronize byte 6 as follows:

- while the incremented heartbeat is at most 60, a value below 44 becomes the cached delay;
- a value at least 44 is replaced by the cached delay; and
- on heartbeat 61, the counter resets and bytes 1..4 become `55 04 00 <delay>`.

The final delay is 60 seconds when `adc_reference < (old_packet_byte_4 >> 2)` and 4 seconds
otherwise. The strict comparison and the uint8 counter wrap are preserved. A received
`55 04` control record schedules the recovered callback after `0x800` ticks; `55 03` has no
functional effect beyond stock logging.

The clean-room implementation is in
`../src/r1_st25dvxxkc.c`. It is a bounded pure
planner: callers provide the ST-reported mailbox-control byte and the existing 23-byte R1
packet, and receive either no action, a send action, or a delayed charge-field action. It
adds explicit frame and packet bounds that the stock internal call path assumed.

## Provider boundary

The following remain external and must not be reconstructed here:

- ST25DVxxKC dynamic-register decoding and mailbox reads/writes, supplied by the pinned
  official ST BSD-3-Clause component;
- Nordic/CMSIS delayed-event execution;
- rectifier ADC acquisition and board electrical behavior; and
- logging and live dock transport.

Host tests cover malformed and short records, mailbox gating, exact version formatting,
first-advertisement framing, both sides of the 44-second cache threshold, heartbeat 61,
strict ADC comparison, uint8 wrap, and both `55` control subcommands. Sanitized host and
freestanding Cortex-M4 builds exercise the same product planner.
