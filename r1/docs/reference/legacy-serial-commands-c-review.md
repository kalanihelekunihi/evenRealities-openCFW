# R1 legacy serial commands in C, 2026-11-11

The locked `r1-2.2.6.0009` application contains BSN command `0x6244e`, SN
command `0x624f4`, cached-record setters `0x7c968` and `0x7c9a8`, the SN
getter `0x7ba78`, and comparison helper `0x5678c`. The source owner
`r1/src/application/board/native_legacy_serial_commands.c` uses the
existing 124-byte `nv_r1` handle. The two setters cap input at 30 bytes,
write the first or second 30-byte field and its length byte, then request
NV idle. The SN getter copies 15 bytes from the second field or returns
15 erased bytes when its length byte is `0xff`. The comparator accumulates
all byte differences and returns one for equality.

Both commands accept selectors zero and one. Selector zero writes 21
request bytes, reads them back, writes the equality result at packet byte
four and sends five bytes. Selector one reads the stored field and sends
25 bytes. The SN command deliberately compares 21 request bytes with a
zeroed 24-byte local whose getter fills only the first 15; a nonzero
request tail makes that comparison fail. Both commands return zero after
the send, regardless of transport result. The BSN command uses the
existing bounded `r1_product_bsn_read` provider for its 21 observable
reply bytes; that provider bounds malformed stored lengths instead of
copying past the reply span.

The ignored host probe at `build/r1-legacy-serial-c-20261111/probe.c`
passed 512 selector cases plus capped-setter, erased-getter and comparator
checks under ASan and UBSan. The R1-only source receipt at
`build/sources-r1-legacy-serial-c-20261111/report.json` compiled 931/931
application and 82/82 bootloader units without failures or duplicate
strong symbols. The strict application receipt at
`build/r1-link-legacy-serial-c-20261111/report.json` has 23 undefined
functions, 639,800 of 696,320 flash bytes used, and no overflow. The
bootloader strict link passes. The later all-device source receipt at
`build/sources-r1-touch-all-20261111/report.json` also passes with the
serial command owner included.

The record read status is ignored as in stock. The setter and SN getter
still depend on a valid cached class; rejected reads and damaged metadata
have no established source-level failure behavior. Hardware execution
and stock byte identity remain unverified.
