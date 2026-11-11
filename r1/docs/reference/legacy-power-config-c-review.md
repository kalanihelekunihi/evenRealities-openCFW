# R1 legacy power configuration command in C, 2026-11-11

The locked application command at `0x62840` dispatches five selectors.
Selector zero persists packet byte four in the four-byte power record and
replies with the readback byte; selector one reads that byte. Selector two
returns the signed 16-bit field at record offsets two and three as two
little-endian packet bytes. Selector three writes the packet halfword into
that field, replacing zero with one, calls the stock no-op hook, and reads
it back. Selector four returns the nonzero-field flag. Other selectors
return zero without sending. The C command in
`r1/src/application/board/native_legacy_reply.c` uses the existing cached
getters and reply sender. The source-owned record setters and no-op hook
are in `r1/src/application/board/native_battery_configuration.c`.

The ignored host probe at `build/r1-power-config-c-20261111/probe.c`
passed all 256 selector cases plus zero-field, full-width setter and hook
checks under ASan and UBSan. The R1-only source receipt at
`build/sources-r1-power-config-c-20261111/report.json` compiled 931/931
application and 82/82 bootloader units without failures or duplicate
strong symbols. The strict application receipt at
`build/r1-link-power-config-c-20261111/report.json` has 21 undefined
functions and uses 640,152 of 696,320 flash bytes without overflow. The
bootloader strict link passes.

The cached-class read status is ignored as in stock. Damaged records,
hardware execution and stock byte identity remain unverified.
