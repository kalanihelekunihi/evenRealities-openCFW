# R1 sleep vivo probe in C

The vivo starter at 0x4a8c8 and timer callback at 0x4a998 now use C. The authorization flag reuses byte 1 of the existing sleep-control owner. Only the adjacent timer word at 0x20006edc is newly allocated; actual stock decompression confirms its zero initializer.

The starter returns if a probe timer exists or health mode is two. Otherwise it enables authorization slot 5, stores the low return byte, and creates a five-second front timer. Creation failure reloads the flag, disables authorization when nonzero and clears it; success logs. An authorization result with a zero low byte still permits timer creation.

The callback checks current health mode. Zero triggers logging and force-wake before the authorization decision. It then reloads the shared flag, disables slot 5 when necessary, releases the incoming timer handle and only then clears the stored probe handle. Provider mutations remain visible at the native decision points.

Stock/C replay passes 1,344 direct and repeated start/stop cases over timer guards, nonzero mode results, low-byte authorization truncation, allocation failure, dynamic logging and flag/handle mutation. Another 840 cases execute the actual C sleep report, activity getter, default callback, force-wake and vivo start/stop bodies together. Nine compiled behavioral defects are rejected. Comparisons include provider order/arguments, call-time state snapshots, guarded shared state, callback identity, preserved registers, SP and masks.

All 748 R1 units compile with no failures or duplicate strong symbols; all 747 prior objects retain their hashes. Relocatable composition has 138 application imports and 34 bootloader imports. The vivo starter import closes with no new imports. Repository-wide source checks pass.

The new probes model authorization, timer allocation/release, health modes, logging and relevant delivery/algorithm boundaries. Direct vivo tests model force-wake internals; the report integration executes the existing force-wake C body. No asynchronous scheduling, physical sensing, complete firmware link or device operation is established. Existing timer-frame assembly is unchanged.

See [machine-readable evidence](sleep-vivo-probe-c-review.json), [REA callback-order receipt](sleep-vivo-probe-c-rea.json) and [stock initialization](sleep-vivo-initialization.json).
