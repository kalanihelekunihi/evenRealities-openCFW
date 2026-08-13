# G2 ux-wear-detect dependency boundary

The three retained-path anchors / 1,126 bytes expand to seven functions /
1,236 body bytes for `app\ux\ux_wear_detect\ux_wear_detect.c`. The complete
physical object is `[0x0049EAD8,0x0049F020)`, 1,352 bytes. Four source-order
helpers missed by Ghidra complete the object: the settings-backed wear-config
getter at `0x0049EAD8`, the `0x107` service-message wear-status sender at
`0x0049EAE2`, a state getter at `0x0049EB8E`, and the wear-state predicate at
`0x0049EB96` (already cited as a provider by the closed service-settings
object). The 116 noncode bytes `[0x0049EFAC,0x0049F020)` are the object-final
literal pool; it holds the retained-path pointer cell `0x0049EFB8`, whose nine
LDR-literal reference sites all lie inside the seven object functions.

Ownership of the leading helpers is proven structurally: `0x0049EAE2` loads
its literal from the object-final pool cell at `0x0049EFAC`, reaching into the
same pool the three anchors use, so no foreign object separates them. The
object ends exactly where the closed ring-connect-policy object begins
(`0x0049F020`); the preceding bytes are the prior object's pool, pinned by a
boundary hash.

Ingress closure records 22 whole-image BL entry sites, one aligned stored
Thumb pointer at `0x006A4754` targeting the message-handler entry
`0x0049ED04` (a dispatch-table slot), zero strict-interior BL decodes, zero
raw interior word collisions, and zero indirect calls.

All 71 external direct calls terminate at admitted EasyLogger (45), bounded
IAR DLIB memory primitives (2), the exact CMSIS-FreeRTOS v10.5.1
`osKernelGetTickCount` wrapper (2 — the sole RTOS seam; no direct FreeRTOS
kernel edge exists), the admitted nanopb iterator helper (1), or first-party
role, settings, display-lifecycle, onboarding, ring-state, service-dispatch,
buzzer, and box/wear-case providers (21). The object embeds no reusable
third-party implementation and adds no version or producing-commit
discriminator. Remaining work is first-party source recreation and wear-sensor
validation; the object is not production-routed. Reproduce with
`python3 tools/analyze_g2_ux_wear_detect.py` and its focused test.
