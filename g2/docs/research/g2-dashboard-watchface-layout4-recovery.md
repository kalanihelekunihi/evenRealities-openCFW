# G2 dashboard watchface layout 4 recovery

The three retained-path anchors / 2,524 bytes expand to 23 functions / 4,184
body bytes for `dashboard_watchface_layout4.c`. The complete physical object is
`[0x005BABA6,0x005BBDA4)`, 4,606 bytes. Twenty restored routines complete
configuration validation, LVGL object construction, time/battery/BLE widget
rendering, and stored lifecycle callbacks.

The audit corrects one important discovery artifact: `0x005BBD10` is object
data, not a function. The callable MSPI cleanup routine begins at `0x005BBD48`,
as independently confirmed by the stored Thumb pointer at `0x0070AFE4`.
Likewise, the raw BL-looking site at `0x004C816C` is the second halfword of the
valid four-byte `sdiv` at `0x004C816A`. The closed inventory therefore has
1,583 instructions, 248 direct calls, eighteen whole-image BL entries, eleven
stored function pointers, no indirect calls, and no strict-interior ingress.

All 230 external calls terminate at admitted EasyLogger (60), LVGL (122), and
AmbiqSuite MSPI helpers (3), bounded IAR DLIB primitives (14), or first-party
dashboard/resource providers (31). This reuses EasyLogger `a596b264…`, LVGL
`344c7c31…`, and the source-equivalent AmbiqSuite 5.1.0 replay `5efc0228…`.
The layout embeds no third-party implementation and adds no new version or
private generating-commit discriminator. Remaining work is first-party
watchface recreation and device display validation; the object is not
production-routed.
