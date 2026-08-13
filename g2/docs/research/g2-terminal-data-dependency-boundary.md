# G2 terminal_data dependency boundary

The four retained-path anchors expand to forty-four functions / 2,902 body
bytes in `[0x005970A8,0x00597C6C)`, a 3,012-byte physical object with 110
noncode bytes (one pool word at 0x00597BE0, a 2-byte pad, and the 104-byte
literal/string pool holding the retained path cell 0x00597C28, the
`terminal.data` tag, and four `terminal_data_*` diagnostic symbols). Forty
source-order functions Ghidra missed restore the complete state-layer of the
terminal feature: session-ring index/reset/append, notification record
find/get/set by session ID, bounded string copy, the 0x84c-byte session
struct accessors, flag and counter getters, the response-timer helpers, the
0x7ff-byte ring writer, and the state sync. Every function has entry
evidence: 180 whole-image BL sites reach starts (152 external, dominated by
the closed `terminal.c` / `terminal_pb_msg_handler.c` UI layer and other
feature modules), one stored interior Thumb pointer at 0x0058B787 reaches the
session-ring reset body, and no stored entry pointer or indirect call exists.

Two raw decode collisions are pinned and disproven as control flow:
0x004925C0 (mid-instruction second halfword inside closed
`service_kvdb_module_configure.c`, `mul` at 0x004925BE) decodes as a BL into
the interior of 0x00597652, and 0x004A4616 (mid-instruction second halfword
inside closed `imu_icm45608.c`, `sdiv` at 0x004A4614) decodes as a BL into
the literal pool. Both sites are proven mid-instruction by the neighbor
objects' own reachable-instruction coverage.

All 45 external calls terminate at admitted EasyLogger (30), bounded IAR
memcpy/memset (13), or the closed `service_time.c` provider (2:
response-timer start and elapsed-time reads). The object uses no
CMSIS-FreeRTOS or FreeRTOS API, embeds no reusable third-party body, and
carries no version/commit discriminator. Remaining work is first-party
source recreation of the terminal state layer and timer/session behavior
validation. Reproduce with `python3 tools/analyze_g2_terminal_data.py` and
its focused test.
