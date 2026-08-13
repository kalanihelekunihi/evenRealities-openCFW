# G2 general-configure dependency boundary

Four retained-path anchors / 854 bytes expand to ten function bodies / 2,376
body bytes for `app\gui\module_configure\general_configure.c`. The physical
object is `[0x00471164,0x00471B9C)`, 2,616 bytes; the preceding neighbor
`drv_mx25u25643g.c` is closed and ends at `0x00471164`, while the following
cluster from `0x00471B9C` onward references the open `sync_info.c` pool
region and is excluded (its calls stay inside its own cluster). Six
source-order bodies restore what Ghidra missed: state getters `0x00471164`
and `0x004711B2`, the singleton thunk `0x0047121C`, the tail-merged body
`0x0047132C`–`0x0047142A` (with genuine secondary entries `0x0047137C` and
`0x0047139C`, each proven by an external BL site and by recovery subsets of
the merged body), the encode helper `0x00471528`, and the 1,032-byte message
handler `0x004716BA` reached through the stored aligned pointer at
`0x006A4534` and referencing the path cell `0x00471ADC` eleven times. Two
pools (22 + 218 noncode bytes) carry the path cell and close the object at
`0x00471B9C`.

The object has 146 direct calls and no indirect call. All 141 external calls
terminate at admitted EasyLogger (110), bounded IAR memory/string primitives
(13), the exact CMSIS-FreeRTOS v10.5.1 `osEventFlagsSet` wrapper (3 at
`0x004495E4`; commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`),
source-admitted nanopb stream decode/encode helpers (8), or bounded
first-party providers (7: OTA scheduling role `0x00465480`, BLE message
transport `0x00475B14`, and closed `service_kvdb_module_configure.c`
persistence `0x0049240E`/`0x004924F6`). No direct FreeRTOS kernel call
exists. The object adds no reusable implementation, version signal, or
observable private producing commit.

Whole-image ingress is closed by 10 BL entry sites (5 internal), one stored
aligned pointer, and two strict interior BL sites reaching the merged body's
secondary entries from `0x005F132A`/`0x005F134A`. No raw interior word
collision exists. Remaining work is first-party general-configure behavior
recreation and settings persistence validation; the object is not
production-routed. Reproduce with `python3
tools/analyze_g2_general_configure.py` and its focused test.
