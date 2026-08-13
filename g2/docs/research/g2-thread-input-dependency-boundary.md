# G2 thread_input dependency boundary

The five retained-path anchors expand to twenty-three functions / 2,090 body
bytes in `[0x00512C84,0x0051357C)`, a 2,296-byte physical object with 206
noncode bytes (two 2-byte alignment pads and the 202-byte literal/string pool
holding the retained path cell 0x005134C4 and the `thread.input` tag).
Eighteen source-order functions Ghidra missed restore the tick reader,
lifecycle enter/exit pair, `INP_ThreadInit` (stored thread descriptor pointer
at 0x007940E8), the thread terminate helper, the record sender plus its five
message-ID send wrappers, `INP_BoxDetectInCase`, three table-dispatched
handlers, `INP_SetTerminalMode`, the queue drain, and the flags dispatcher.
Twenty whole-image BL sites reach starts (7 external: touch driver, buzzer,
gesture, and UI callers); one stored entry pointer; no strict interior ingress
and no pseudo-BL into the pool.

The single indirect call at 0x00512FC6 is a bounded runtime dispatch:
`INP_MessageProcesser` matches message IDs against a five-entry
`{uint16 id, handler}` table in `.bss` (input state struct 0x2000408C+0x24)
populated only through runtime registration; the table base cell is referenced
from this object alone.

All 127 external calls terminate at admitted EasyLogger (90), bounded IAR
memset (3), exact CMSIS-FreeRTOS v10.5.1 wrappers (10: osThreadNew,
osThreadTerminate, osThreadFlagsSet, osThreadFlagsWait, osDelay,
osMessageQueueNew/Put/Get/Delete — the same seam set as thread_ring.c), the
source-owned runtime wrapper (1), closed thread-manager lifecycle providers
(3), closed first-party service/driver providers (9: ring_service, ux_system,
nvdb_product_mode, drv_buzzer, service_gesture_processor, service_touch_dfu),
or bounded frontier-open first-party providers (11: tick readers and the
drv_cy8c4046fni.c touch driver). No direct FreeRTOS kernel call exists. The
object embeds no reusable third-party body and no version/commit discriminator.
Remaining work is first-party source recreation and touch-gesture behavior
validation. Reproduce with `python3 tools/analyze_g2_thread_input.py` and its
focused test.
