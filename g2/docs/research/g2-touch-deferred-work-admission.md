# G2 touch deferred work (batch 17)

Batch 17 admits the 92-byte deferred-work function at `0x0780` as isolated
MIT clean-room source. The function snapshots two pending flags and a captured
value while holding the injected critical-section boundary, clears both flags,
then dispatches the notification and configuration-load callbacks after leaving
the critical section.

The complete authenticated call closure is `0x0738`, `0x0BE0`, `0x0D4C`,
`0x1192`, and `0x119A`. Critical-section and notification behavior remain typed
callbacks, configuration loading is the admitted MIT Batch 16 seam, and the
shipped logger is an intentional no-op. No Em_EEPROM EULA body, resident table,
or MMIO behavior is admitted.

Host tests cover atomic snapshot/clear order, both independent dispatch flags,
missing-provider fail-closed behavior, and Cortex-M0+ symbol closure. The
concrete gap falls from 55 functions / 4,964 bytes to 54 / 4,872 bytes;
application contracts fall from 43 to 42. All twelve external/unavailable
functions, resident loaders, EULA provider bodies, system/halt boundaries, and
`0x1B6C`/`0x1C54`/`0x2638` remain unadmitted.

This source is isolated and not production-routed. Hardware validation remains
blocked by unavailable physical evidence. The analyzer also regenerates the current Touch
readiness summary so downstream completion audits consume Batch 17 counts.
