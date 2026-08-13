# G2 box-detect service dependency boundary

Three retained-path anchors / 876 bytes expand to thirty-two functions /
3,564 body bytes for `platform\service\box_detect\service_box_detect.c`. The
physical object is `[0x004ABEC8,0x004ACE10)`, 3,912 bytes, closed on both
sides by already-closed neighbors (`service_nvdb_product_mode.c` ends at
`0x004ABEC8`; `charger_common.c` starts at `0x004ACE10`). Twenty-nine
source-order functions restore what Ghidra missed, including the state
accessor cluster `0x004AC59A`–`0x004AC776`, the static helpers `0x004AC776`
and `0x004AC798` (shared by the anchored init/update bodies), the timer
wrapper `0x004AC828`, the tiny getters `0x004ACAA0`–`0x004ACAD0`, and the
518-byte message handler `0x004ACB40` that itself references the retained
path through cell `0x004ACDBC` and is reached through the stored aligned
callback pointer at `0x006A4614`. A second stored aligned pointer at
`0x007490D8` reaches the big state machine `0x004AC278`. Eight pool regions
(348 noncode bytes) carry both path cells and are referenced only from inside
the object.

The object has 209 direct calls and no indirect call. All 172 external calls
terminate at admitted EasyLogger (130), bounded IAR memory primitives (7),
exact CMSIS-FreeRTOS v10.5.1 timer wrappers (13), or bounded first-party
providers (22). The CMSIS-FreeRTOS seams are exact and enumerated:
`osTimerNew` x2 (`0x004493B0`), `osTimerStart` x2 (`0x00449498`),
`osTimerStop` x6 (`0x004494D8`), `osTimerIsRunning` x1 (`0x00449522`),
`osTimerDelete` x2 (`0x0044953E`) — commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`; no direct FreeRTOS kernel call
exists. First-party targets include ring-service `0x0047243A`, display
manager `0x00474100`/`0x0047432C`, device manager `0x004C659A`, product-mode
persistence `0x004ABE60`, glasses-case protobuf service `0x00510A0C`/
`0x00510DEC`, the unclaimed interstitial function `0x00510FE2` between two
closed objects, and open `thread_input.c` body `0x005130A6`. The object adds
no reusable implementation, version signal, or observable private producing
commit.

Whole-image ingress is closed by 65 BL sites (39 internal) and the two stored
aligned pointers above. No strict interior BL and no raw interior word
collision exists. Remaining work is first-party box-detect state-machine
recreation and case/box hardware validation; the object is not
production-routed. Reproduce with `python3
tools/analyze_g2_service_box_detect.py` and its focused test.
