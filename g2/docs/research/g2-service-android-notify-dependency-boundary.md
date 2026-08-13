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

## Flagged embedded third-party candidate

Thirteen calls terminate at an unadmitted JSON parser body at 0x004D79FA /
0x004D7F7E / 0x004D83AA (Ghidra-missed code between `service_whitelist.c` and
`pb_service_notification.c`). The body shows cJSON-class structure: a
null/true/false literal pool at 0x0078D15C, a linked-node get-item walk, and
parse wrappers. The same provider is used by the already closed
`service_whitelist.c` (19 call sites). No version string or producing commit is
recoverable from the image, so it is recorded as a flagged embedded
third-party body candidate — not silently absorbed into admitted providers —
and no new version/commit discriminator is claimed.

The object adds no other reusable implementation or version signal. Remaining
work is first-party source recreation of the JSON message handling and
validation against dual-glasses sync behavior. Reproduce with
`python3 tools/analyze_g2_service_android_notify.py` and its focused test.
