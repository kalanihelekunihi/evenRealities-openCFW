# G2 service_android_notify dependency boundary

The three retained-path anchors expand to five functions / 972 body bytes in
`[0x0048E484,0x0048E8D4)`, a 1,104-byte physical object with a 132-byte rodata
pool (33 words: format strings, the retained path cell 0x0048E858, the
`svc.android_notify` tag, and the registered `_rxSyncEventCallback` pointer at
0x0048E878). Two source-order functions Ghidra missed restore the ANCC sync
forward (stored init pointer at 0x006A46C4) and the sync event callback. Three
whole-image BL sites reach starts: one external (0x004578E2 into
`SVC_ANDROID_ParseNotification`) and two intra-object; no strict interior
ingress, no pseudo-BL into the pool, no indirect calls.

All 65 external calls terminate at admitted EasyLogger (40), bounded IAR DLIB
primitives (7: memset/string op), the already closed `service_ancc.c` object
(2), the closed AmbiqSuite 5.1.0 ANCC profile route (1, commit
de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f), the closed `service_whitelist.c`
object (1), or the closed `sync_interface_api.c` provider (1). The object uses
no CMSIS-FreeRTOS or FreeRTOS kernel API at all — unlike its sibling
`service_ancc.c` it holds no mutex.

## Production-routed embedded third-party provider

Thirteen calls terminate at the cJSON parser body at 0x004D79FA /
0x004D7F7E / 0x004D83AA (Ghidra-missed code between `service_whitelist.c` and
`pb_service_notification.c`). The body shows cJSON-class structure: a
null/true/false literal pool at 0x0078D15C, a linked-node get-item walk, and
parse wrappers. The same provider is used by the already closed
`service_whitelist.c` (19 call sites). Four binary discriminators bound it to
DaveGamble cJSON v1.7.9 through v1.7.12. OpenCFW selects authenticated tag
v1.7.12 (`3c8935676a97c7c97bf006db8312875b4f292f6c`) and now routes all 21 linked
parse-side functions through maintained freestanding C in both compiler
profiles. The route has 21 strict entry redirects, no undefined symbols, and
preserves the fixed SRAM allocator-hook and parse-error ABI. The exact private
historical checkout within the source-identical interval remains
binary-unobservable; that provenance limitation is not a software gap.

The object adds no other reusable implementation or version signal. The
retained first-party JSON message handling remains blocked by unavailable
proprietary inputs, and live dual-glasses sync validation is blocked by
unavailable physical evidence. Reproduce with
`python3 tools/analyze_g2_service_android_notify.py` and its focused test.
