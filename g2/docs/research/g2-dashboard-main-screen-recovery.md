# G2 dashboard main-screen recovery

The eight retained-path anchors / 3,458 bytes for the misspelled stock path
`app\gui\dashboard\screens\ui_DashBaord_Main_Screen.c` expand to 31 functions /
9,040 body bytes. The complete physical object is
`[0x004E772C,0x004E9DD4)`, 9,896 bytes including 856 bounded noncode bytes.
Seventeen pathless functions complete the constructor, widget composition,
input/animation callbacks, and dashboard resource dispatch.

The object also demonstrates why object closure cannot rely on ordinary
function starts alone. Thirteen stored pointers select whole-function entries,
while seven more select two authenticated interior callback labels created by
compiler tail merging. Six other unaligned words merely equal odd addresses
whose even values are second halfwords of 32-bit instructions, so the audit
pins them as pseudo-pointers rather than callable entries. No BL enters a
strict interior address. The audit covers 3,353 instructions, 542
direct calls, 49 whole-image BL entries, and no indirect calls.

All 519 external calls terminate at admitted or bounded providers: EasyLogger
(255), LVGL (146), CMSIS-FreeRTOS (2), IAR DLIB (7), and 109 first-party
dashboard/widget/service edges. The object reuses LVGL commit `344c7c318…`,
CMSIS-FreeRTOS `d213f261…`, FreeRTOS-Kernel `def7d2df…`, and EasyLogger
`a596b264…`; it embeds no utility definition or new version discriminator.
The remaining work is clean-room dashboard policy/UI recreation and device
validation, and the object is not production-routed.
