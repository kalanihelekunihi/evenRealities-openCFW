# Touch calibration and report — offline reconstruction

Independent instruction-derived C for saved-baseline getter0x3a1c, save0x3a38,
gesture initialization0x404c, proximity transition0x441c, report/calibration0x3b24,
and sensor/widget status queries0x7d36/7d04. Additive offline ARM32 guest module;
not linked into production firmware. Source composes preserved EEPROM modules.

The report path still executes **original gesture machine0x4070** and its speed
helper by address. This is an explicit executable dependency, not fully source
closure or a distributable/deployable replacement. Sensor type/pointer/sample
fixtures are bounded; analog scanning and physical timing are not validated.
See [analysis report](../../../analysis/touch-calibration-closure-2026-10-08/REPORT.md)
for original/native results and exact limits.
