# Unchanged GNU14.2.1 GPIO family comparison

Predeclared selection and boundaries are preserved in `SELECTION.md`; no flags,
inputs or selected functions were retuned. Same authenticated14.2.1 toolchain,
PDL pin and prior options/header environment; new translation unit `cy_gpio.c`.

| Function | Declared target bytes | Compiled section | Result |
| --- | --- | --- | --- |
| SetHSIOM | 52 | 60 | predeclared complete-section mismatch; all52 overlapping bytes agree |
| Write | 32 | 32 | exact, no relocations |
| SetDrivemode | 58 | 58 | exact, no relocations |
| SetInterruptEdge | 36 | 36 | exact, no relocations |
| Pin_Init | 174 | 188 | non-exact, call relocations unresolved |

This yields three exact predeclared sections (126bytes) in a third PDL source
translation unit. Known function candidates remain selected attribution
evidence, not independent discovery, unique compiler identification or complete
touch reconstruction. Full inputs, outputs, lengths, mismatch positions and
relocation-section presence are in `results.json`. Pin_Init raw-byte equality
is explicitly not claimed and no fitting link experiment was performed.

The SetHSIOM negative prompted a separately labeled code/data-accounting
follow-up, not retrospective alteration of the predeclared result. Its complete
60-byte section exactly matches stock `[0x8E28,0x8E64)`, including the8-byte
gap after historical code endpoint0x8E5C. `pool-followup.json` records both
hashes and marks independent literal-pool classification review required.
Historical symbols remain untouched. This illustrates why code-only extents
must not be equated automatically with complete compiler sections.

Pin_Init is the current concrete boundary: relocation targets and full
code/padding/literal extent need independently verified linkage accounting
before a compiled-source match can be assessed. No arbitrary source/flag
changes are justified. Independent review is pending; no admission, production,
device, Git or campaign-state change occurred. Approved Docker uses the same
nonprivileged network-disabled/minimal-mount controls as prior comparisons.
