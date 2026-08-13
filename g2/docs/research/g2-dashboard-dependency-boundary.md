# G2 dashboard dependency boundary

The two retained-path anchors / 760 bytes expand to twenty-four functions /
10,040 body bytes for `app\gui\dashboard\dashboard.c`. The complete physical
object is `[0x0049C070,0x0049EAD8)`, 10,856 bytes. Ghidra discovered three
functions (`0x0049C146`, `0x0049C3D8`, `0x0049C5BC`); twenty-one source-order
routines were restored, completing the dashboard lifecycle, configuration
dispatch, screen/page event routing, and the stored callback table.

## Extent and boundaries

The object opens exactly where the closed `pb_service_setting.c` interval
`[0x0049B198,0x0049C070)` ends and closes with its own trailing literal pool
at `0x0049EAD8`. The following bytes are `ux_wear_detect.c` functions
(`0x0049EAD8`, `0x0049EAE2`): every BL site targeting them lies in the
wear-detect cluster (`0x0049EB70`–`0x0049EC8C`, `0x0049EF0E`–`0x0049EFA2`) or
far callers, never in the dashboard body, so they are excluded. The trailing
pool holds the fifth dashboard path-pointer cell `0x0049EA64`, referenced only
by dashboard code, plus the four-entry local callback table at
`0x0049EA90`–`0x0049EA9C` binding `0x0049E486`, `0x0049C2B0`, `0x0049C3D8`,
and `0x0049C5C4`. Boundary slices of 16 bytes on both sides are hash-pinned.

## Function inventory and embedded pools

Twenty-four functions are pinned in source order. Function
`0x0049CE14`–`0x0049DD46` (3,890 bytes) carries two embedded literal pools,
`[0x0049DB46,0x0049DB5C)` and `[0x0049DBF6,0x0049DC10)` (48 bytes including
two `0xBF00` alignment pads): each follows an unconditional forward branch and
every 4-aligned word is referenced by an `ldr`-literal inside the same
function, proving they are mid-function pool spills, not function boundaries.
All other functions are fully flow-covered with no embedded data. Seven
inter-function literal pools (816 noncode bytes) complete the physical object.

One recovered function, `0x0049E144`–`0x0049E40A` (710 bytes), has no static
ingress anywhere in the image: no direct BL site, no stored entry pointer, no
stored interior word, and no `movw`/`movt` constant pair names it. It sits
between two dashboard pools, logs through dashboard path cells
`0x0049E440`/`0x0049EA64`, and calls four dashboard-internal helpers
(`0x0049C7FE`, `0x0049C89E`, `0x0049C93E`, `0x0049CB50`), so it is retained
as an unreferenced global kept by the linker; the audit asserts it never
gains an entry.

## Ingress closure

Thirty-five whole-image direct BL entry sites (sixteen external to the
physical object) and six stored function entry pointers are pinned: four in
the trailing-pool callback table and two ROM data cells `0x006A44E4` /
`0x006A44E8` binding `0x0049DDB8` and `0x0049E68C`. No strict-interior ingress
exists. One raw unaligned BL decode at `0x004A5BBC` targeting interior
`0x0049C1CC` is proven a mid-instruction window: the aligned four-byte `udiv`
at `0x004A5BBA` covers the site. Six stored odd words into function interiors
are all non-4-aligned pseudo-pointer windows, not linker-emitted cells.

## Provider boundary

All 598 external direct calls terminate at admitted providers: EasyLogger
(370), LVGL (43), IAR DLIB (48), CMSIS-FreeRTOS (13), nanopb (1), and
first-party providers (123 across 49 bounded entries). The exact RTOS seams
are the CMSIS-FreeRTOS v10.5.1 wrappers `osMutexNew` (`0x0044971C`, 1 call),
`osMutexAcquire` (`0x004497B6`, 6 calls), and `osMutexRelease` (`0x0044981C`,
6 calls) over the admitted FreeRTOS kernel; no direct kernel call occurs. The
single nanopb edge reuses the admitted helper `0x0048949C`. First-party edges
cover the display thread, sync framework/interface, time/settings services,
ring BLE status/battery callbacks, dashboard screens (main screen, stock,
calendar, news pages), dashboard data process, watchface manager, and the
dashboard extension object. `0x004FDF08` and `0x004FDF74` log through the
`dashboard_data_process.c` path but lie before its closed interval; they are
bounded first-party providers outside that closure.

This reuses EasyLogger `a596b264…`, LVGL `344c7c31…`, CMSIS-FreeRTOS
`d213f261…`, FreeRTOS `def7d2df…`, and nanopb `98bf4db6…`. The object embeds
no third-party implementation and adds no new version or private
generating-commit discriminator.

## Limitations

The twenty-one restored functions carry source-order and call-graph evidence
only; their original C names are unobservable. The zero-ingress function could
still be reached through a runtime-computed table built by arithmetic rather
than a ROM constant; no such construction was identified. The object is not
production-routed; first-party dashboard recreation and device display
validation remain open work.
