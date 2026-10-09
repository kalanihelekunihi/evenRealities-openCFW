# IMO configuration and HF frequency linkage

Unchanged authentic public-source ImoSetFrequency `[0x9C80,0x9D90)` matches
272 bytes, and ClkHfGetFrequency `[0x9F9C,0x9FD4)` matches56bytes.
These328new selected bytes await review. All included source/assembly
dependencies also match;120reusedbytes are excluded from new counts.

ImoSetFrequency validates its requested frequency, compares current frequency,
calculates a trim/configuration value using unsigned division, disables IRQs,
programs oscillator control/trim registers with source delay calls, restores
PRIMASK, and performs the final delay. Exact stock calls are recorded in
`results.json`. No calibrated physical frequency or elapsed delay is inferred.

ClkHfGetFrequency reads the HF divider field, obtains the selected source's
software frequency from IMO or external-clock providers, and shifts by the
divider selection. Unsupported source returns zero. The external provider is
a configured software word, not a hardware frequency measurement.

The division call is bound to the instruction-proven original target `0xA6C0`
without supplying an executable body/stub. It remains an explicit compiler
runtime boundary; this comparator is not a complete executable source rebuild.
No source/flags fitted, device writes, runtime execution or campaign admission.
