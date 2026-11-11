# R1 system-control command 0x37 in C, 2026-11-11

`r1/src/application/board/native_system_control_37.c` implements stock
`0x628f6` for selectors 0..5, 13, `0xfd`, `0xfe`, and `0xff`. It preserves the
five-, eight-, ten-, and variable-length reply paths. Selector two reads the
cached configuration byte, writes `0x5a`, acknowledges, deletes peers, delays
200 ticks, then either runs the existing system-control thunk for prior
`0x55` or records reset tag four and resets. Selector three acknowledges
before testing its byte-one reset request; selector five writes `0x55`, delays,
records reset tag six and resets. Selector four returns the device identity.
Unknown selectors return zero without a reply. The cached byte setter is stock
`0x7c93c` in `r1/src/application/runtime/native_device_configuration.c` and
updates offset 112 of the existing 124-byte record.

The ignored host probe at `build/r1-system-control-37-c-20261111/probe.c`
covers all 256 selectors plus the low-word clamp and both reset branches. It
checks reply length/content, configuration write, peer delete, delay, reset
tags and the branch to the system-control thunk. AddressSanitizer and
UndefinedBehaviorSanitizer pass. Reset is intercepted in the host probe;
actual reset-vector behavior and physical board execution remain unverified.

`build/sources-r1-system-control-37-c-20261111/report.json` compiles 936/936
application and 82/82 bootloader units with no known failures or duplicate
strong symbols. The strict application receipt at
`build/r1-link-system-control-37-c-20261111/report.json` has 15 undefined
functions and uses 642,656 of 696,320 flash bytes without overflow. The
strict bootloader receipt at
`build/r1-boot-link-system-control-37-c-20261111/report.json` links with a
valid vector. Byte identity and hardware behavior are not established.
