# R1 legacy device-info command in C, 2026-11-11

The locked application command at `0x62a5c` has five reply selectors:
BSN, SN, temperature and accelerometer calibration, a 43-byte
configuration record, and a 20-byte flash-geometry report. The C owner at
`r1/src/application/board/native_legacy_device_info_command.c` reuses
the existing source-owned BSN/SN getters, temperature getter and reply
sender. It reads UICR `NRFFW[0]` (`0x10001014`), FICR `CODEPAGESIZE`
(`0x10000010`) and FICR `CODESIZE` (`0x10000014`) in stock order before
dispatch. The 20-byte report stores those words, selects the bootloader
address or the product of page size and page count when UICR is erased
(`0xffffffff`), then stores that flash limit and the limit minus 36 pages.
The configuration reply copies the four-byte request header, fills 36
bytes with `0xff`, and appends the three cached configuration bytes.

The two additional cached-record readers at stock `0x7b9c8` and `0x7ba24`
live in `r1/src/application/runtime/native_device_configuration.c`. They
read six accelerometer-calibration bytes at offsets 68..73 and the
configuration byte at offset 112 of the existing 124-byte `nv_r1` record.

The ignored host probe at
`build/r1-device-info-command-c-20261111/probe.c` passed all 256 selectors
and the erased-UICR flash-limit branch under ASan and UBSan. It exercised the
real source BSN/SN and cached-record readers; the temperature getter and
legacy sender were modeled at their call boundaries. The R1-only source
receipt at `build/sources-r1-device-info-geometry-c-20261111/report.json`
compiled 934/934 application and 82/82 bootloader units without failures
or duplicate strong symbols. The strict application receipt at
`build/r1-link-device-info-geometry-c-20261111/report.json` has 17
undefined functions and uses 641,696 of 696,320 flash bytes without
overflow. The bootloader strict link passes.

The cached-class read status is ignored as in stock. The host probe does
not execute the fixed UICR/FICR reads; their physical values,
hardware behavior, malformed record policy and stock byte identity remain
unverified.
