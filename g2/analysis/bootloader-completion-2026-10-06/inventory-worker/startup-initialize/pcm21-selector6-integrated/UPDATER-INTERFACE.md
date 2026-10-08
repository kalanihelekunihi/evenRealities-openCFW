# Locked PCM2.2 power updater interface

Stock entry0x42a878, extent758 bytes; compiler symbol opencfw_boot_spotmgr_power_state_update_a. Entry wrapper0x41cd1a truncates R0 stimulus/R1 flag to8 bits and forwards R2 argument pointer to table20026e3c. Revision35/variant2 and36 install PCM2.2;34/2 and35/1 install PCM2.1. Tests assert actual relocated guest pointers; comparison normalization never changes the guest table.

| Stimulus | Argument | Snapshot action |
|---|---|---|
|0 CPU|byte requested state|CPU change/shortcut/deep transition|
|1 GPU|byte requested state|replace GPU state|
|2 temperature|three aligned words: input float bits, lower output, upper output|classify; write output bounds; class4 returns6|
|3 device|aligned mask word|OR device mask only when flag nonzero|
|4 audio|aligned mask word|OR audio mask only when flag nonzero|
|5 memory|aligned word|replace memory regardless of flag|
|6 SSRAM|aligned word|replace SSRAM only when flag nonzero|
|7+|none valid in this locked branch|returns6 in active valid state|

Snapshot fields are32-bit device/audio/memory/SSRAM at0/4/8/12, then byte temperature, signed byte CPU and GPU at16/17/18 (aligned C size20). Source/header is startup_events_a.h. Address names distinguish inferred hardware meanings from verified layout.

SIMOBUCK status not3 returns0 before processing. Missing profile magic1f01600d returns1. Required null argument returns6; flags-off mask stimuli need not dereference arguments. Original CPU states2/3/4 -> requested0/1 shortcut updates CPU global without full transition. HP-to-LP native fixture routes selector6 with arguments[5,13,6,7]. Do not generalize that one configuration to all profiles.

Flag fixtures use canonical0/1 through the truncating wrapper. The raw source function currently tests the full uint32 flag as truthy; arbitrary direct calls with high bits (e.g.256) are not established equivalent to stock byte truncation. This is an additional explicit ABI boundary, separate from the validated wrapper paths.

Temperature bounds are binary32 values, with public HAL giving temperature interpretation; timer delay/poll values are not physical elapsed-time proof. Source FP comparisons remain incomplete for exception/control side effects; see fp-architecture/REPORT.md. Unsupported transition slots remain contracts and raise in strict native tests, rather than receiving invented returns.
