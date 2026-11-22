# Touch calibration and report — offline reconstruction

Independent instruction-derived C for saved-baseline getter0x3a1c, save0x3a38,
gesture initialization0x404c, proximity transition0x441c, report/calibration0x3b24,
and sensor status query0x7d36. The exact upstream CapSense C provider owns
the widget status query0x7d04. The source-linked touch image
uses this module and composes the preserved EEPROM source units.

The report path calls the source-owned gesture machine0x4070 and its C speed
helper. Sensor type/pointer/sample fixtures are bounded; analog scanning and
physical timing are not validated.
The report and main loop call `Cy_CapSense_IsWidgetActive` directly; the
duplicate local `touch_widget_active` implementation was removed. See
[`touch-capsense-cardinalities-and-widget-provider-20261111.json`](../../../evidence/touch-capsense-cardinalities-and-widget-provider-20261111.json).
See analysis report (`pre-consolidation:g2/analysis/touch-calibration-closure-2026-10-08/REPORT.md`)
for original/native results and exact limits.
