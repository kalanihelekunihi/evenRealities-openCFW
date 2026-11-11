# R1 factory-mode legacy subcommand in C, 2026-11-11

The locked application dispatcher at `0x62388` reads the existing
configuration byte before every selector. Selector zero starts factory
mode when bit `0x10` is clear; when set it writes `0x12,0x34` to the packet
and sends six bytes if the passed handle is valid. Selector one clears the
32-byte response span, reads the configuration byte again and sends five
bytes. Selector two stops factory mode, reports success as one or zero,
and sends five bytes. Selector three returns the four-byte configuration
word in an eight-byte response. Selector four stops factory mode and
clears both configuration fields without replying. Unknown selectors
return zero. Selectors zero through three suppress the send when the
passed handle is `0xffff`, independently of the global legacy sender.
The C body is in `r1/src/application/board/native_legacy_reply.c` and
reuses source-owned factory-mode and cached-record providers.

The ignored host probe at `build/r1-legacy-subcommand-c-20261111/probe.c`
passed all 256 selectors, the start path, invalid handles and a zero stop
result under ASan and UBSan. The R1-only source receipt at
`build/sources-r1-legacy-subcommand-c-20261111/report.json` compiled
932/932 application and 82/82 bootloader units without failures or
duplicate strong symbols. The strict application receipt at
`build/r1-link-legacy-subcommand-c-20261111/report.json` has 19 undefined
functions and uses 640,800 of 696,320 flash bytes without overflow. The
bootloader strict link passes. Physical factory-mode behavior and stock
byte identity remain unverified.
