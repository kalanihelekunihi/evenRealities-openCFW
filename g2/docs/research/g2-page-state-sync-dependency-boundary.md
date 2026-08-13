# G2 dashboard page-state-sync dependency boundary

Six retained-path anchors / 1,016 bytes expand to eight functions / 1,244 body
bytes for `app\gui\dashboard\page_state_sync.c`. The physical object is
`[0x004FFE14,0x00500378)`, 1,380 bytes, closed on both sides by already-closed
neighbors (`health.c` ends at `0x004FFE14`; `cb_ring_battery.c` starts at
`0x00500378`). Two source-order functions at `0x004FFE14` (a diagnostic setter
that itself references the retained path) and `0x004FFEB4` (a watchface-kind
writer calling the closed six-byte dashboard getter `0x00558142`) restore what
Ghidra missed ahead of the anchored cluster `0x004FFEF8`–`0x005002F0`. The
136-byte tail pool carries the path pointer cell `0x005002FC`; all 34 pool
words are referenced only from inside the object.

The object has 62 direct calls and no indirect call. All 57 external calls
terminate at admitted EasyLogger (50), bounded IAR memory primitives (3), the
source-admitted nanopb `pb_istream_from_buffer` initializer (1), or bounded
first-party providers (3: peer sync transport `0x0045A570`, closed
dashboard-data-process writer `0x004FF7DC`, watchface kind getter
`0x00558142`). No CMSIS-FreeRTOS or FreeRTOS kernel seam exists. The object
adds no reusable implementation, version signal, or observable private
producing commit.

Whole-image ingress is closed by 27 BL sites (5 internal to the object, all
reaching the shared diagnostic prologue `0x004FFEF8`). No stored function
pointer and no strict interior BL exists. Twenty-two raw aligned/unaligned
words in the string/resource regions coincide with Thumb-interior values
(`0x0050000B`–`0x005000F3` windows) and are scanner coincidences, not
pointers. Remaining work is first-party source recreation and dashboard
page-state behavior validation; the object is not production-routed.
Reproduce with `python3 tools/analyze_g2_page_state_sync.py` and its focused
test.
