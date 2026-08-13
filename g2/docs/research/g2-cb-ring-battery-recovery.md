# G2 ring-battery callback facade recovery

The retained `platform\service\callback_mgr\cb_ring_battery.c` path had no
function in the baseline path census because its only path-referencing body
was missed by Ghidra. Raw source-order recovery closes five functions / 122
body bytes plus a 30-byte pool at `[0x00500378,0x00500410)`. The next halfword
is the prologue of a different callback. Six direct entries, ten body calls,
both boundaries, and the absence of indirect, stored, or strict-interior
ingress are pinned by the analyzer.

The facade owns generic callback list `0x20073F90` with retained type string
`RING_BAT_INFO`. It initializes/deinitializes that list, rejects a null
registration, registers valid callbacks, and publishes an event key with an
in/out value word. The latter is the exact 14-byte target used by
`UX_BatterySyncHandler` for changed level key 0 and charging key 1.

Five of ten calls are already admitted EasyLogger diagnostics. The others are
one first-party forwarding target and four generic callback-manager operations;
there is no CMSIS-FreeRTOS call or embedded third-party definition. Exact
public searches for the retained callback symbol and filename produced no
source candidate, so this object adds no version discriminator and cannot
reveal the private generating commit. It is not yet production-routed.
