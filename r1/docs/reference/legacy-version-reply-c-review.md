# R1 legacy replies in C, 2026-11-11

The stock application function at `0x62584..0x625a7` reads packet byte 3.
Selectors 0 and 1 copy the ten-byte literals at `0x625a8` and `0x625b4`
into packet bytes 4–13; every other selector leaves those bytes unchanged.
All paths tail-call the existing `0x8967c` legacy reply with length 14.
This was checked against the pinned official R1 2.2.6.0009 application image
(SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`).

`r1_legacy_cmd_version_reply` now implements that behavior in
`r1/src/application/board/native_legacy_reply.c`, which already owns the
reply sender. The same module now owns the stock `0x62834` fixed `0xff`
status response, `0x628ae` NFC field query, `0x4e1f8` pair-hook
cancellation response, and `0x62546` battery-type reply. The NFC query returns zero without
querying or replying for nonzero selectors. The stock command router passes
the handle in `r0` and packet pointer in `r1`; these signatures preserve that
ABI even though the shared reply sender gets the current handle itself.

The ignored `build/r1-legacy-version-c-20261111/probe.c` exercises all 256
version selectors, all 256 NFC selectors, all 256 cancellation selectors,
five charger states across all 256 battery selectors, and the fixed status
response with
AddressSanitizer and UndefinedBehaviorSanitizer. Packet bytes, reply lengths,
queue return narrowing, the NFC getter call count, and the exact pair-hook
cancellation callback pass. The battery cases verify charge-state and cached
battery-byte calls and the three distinct response values. The manifest
origin includes all six stock functions in this module. Both legacy routers
now call these C functions.
