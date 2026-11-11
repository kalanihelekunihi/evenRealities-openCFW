# R1 touch long-press command in C, 2026-11-11

The locked application command at `0x62b4c` sends a seven-byte legacy
reply for every selector. Only selector one reads the big-endian request
halfword, writes one to packet byte four, emits the configured log, and
calls the clamp at `0x8e880`. The clamp stores accepted values from 100
through 3,000 milliseconds in the source-owned
`r1_touch_long_press_threshold`. Values above 3,000 become 1,000; values
below 100 become 100. The stock low-value diagnostic still says “set to
50,” and the C source preserves that text. The source owner is
`r1/src/application/board/native_touch_long_press_command.c`; its
threshold is owned by the existing touch-slider source.

The ignored host probe at `build/r1-touch-long-press-c-20261111/probe.c`
passed all 256 selectors and seven clamp/log boundary cases under ASan
and UBSan. The R1-only source receipt at
`build/sources-r1-touch-long-press-c-20261111/report.json` compiled 932/932
application and 82/82 bootloader units without failures or duplicate
strong symbols. The strict application receipt at
`build/r1-link-touch-long-press-c-20261111/report.json` has 20 undefined
functions and uses 640,640 of 696,320 flash bytes without overflow. The
bootloader strict link passes.

The stock clamp leaves an incidental RAM base pointer in R0; its known
caller ignores that value, so the C clamp exposes only its threshold and
log effects. Physical timing, hardware execution and stock byte identity
remain unverified.
