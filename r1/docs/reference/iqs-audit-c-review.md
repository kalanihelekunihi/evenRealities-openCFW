# C IQS error audit and bounded formatter entries

`r1/src/application/runtime/native_iqs_audit.c` implements the recovery audit at
`0x41a40`. The existing recovery caller now resolves to this C body. It updates
RAM state and reads channel data; it performs no persistent-storage write.

Every call increments the unsigned sequence, reads ticks, then reloads sequence.
Sequence 1 or an unsigned elapsed interval of at least 10,000 ticks proceeds;
other calls return after the sequence increment. The report tick is stored
before model and port calls. The audit clears 48 sample bytes and reads E3 for
42 or 48 bytes, capturing the model pointer before the read. A configuration
byte ff at offset 5+channel excludes that channel; a null configuration includes
every channel. It computes active/min/max values and appends unsigned values
while the signed text offset is below 152. Header sinks independently decode SN,
read the captured configuration halfword and reload sequence. Logging modes
are read live. The geometry string is 8x3 only for 24 channels.

The two narrow state owners at `0x2000773c` and `0x20007740` match authenticated
cold RW and compiled initializers. Existing model configuration and channel
count providers remain shared. All-masked channel lists now have defined empty
C output; native unwritten private list bytes are excluded from equivalence
claims. Sample buffers are cleared in both versions, allowing direct partial-read
comparisons, including failed read statuses.

The audit uses the existing formatting core. Its `snprintf` and `vsnprintf`
assembly entry bridges are replaced by ordinary C variadic functions. The
selected Arm AAPCS single-pointer `va_list` representation is checked at compile
time and copied through object representation, without a compiler field-name
dependency. Private saved registers/frame addresses are not ordinary API outputs.
The retained logger now explicitly converts its saved raw argument stream to
the typed `va_list` before calling the C wrapper.

The [machine-readable review](iqs-audit-c-review.json) records:

- 1,354 direct audit stock/C comparisons: unsigned sequence/tick wrap, the exact
  interval boundary, masks, sample-position limits, live provider mutations,
  partial reads, controlled formatter returns and seeded cases.
- 1,108 comparisons executing actual C formatter, IQS ports, touch transport and
  registry against prepared callbacks. Each audit pass additionally checks six
  independent statistics oracles and fourteen C empty-list sink cases.
- 2,916 formatter comparisons through the actual C core: both entries, capacity
  boundaries, literal/escaped formats, 32/64-bit alignment, mixed/stars/string
  arguments, character/count writes and sampled binary64 formats.
- 224 retained-logger comparisons through its final C body and formatter, using
  cold/warm contexts, cursor boundaries, raw mixed-width streams and callback
  return values.
- Thirteen rejected compiled defects. The final retained caller is tested
  separately; all previously tested audit/formatter/provider objects are
  unchanged in the final build.

Integer/FP callee saves, stack guards, PRIMASK and BASEPRI are checked. Standard
copy/fill operations are modeled due to the earlier recorded Unicorn return/
IT-state issue. Ticks, SN/model queries, logging, kernel/device callbacks, crash
initialization and stdout are controlled where applicable. These checks do not
prove physical transfers, flash behavior, all formatting semantics, other
existing variadic bridges, or a full call-chain stack budget.

The [REA review](iqs-audit-rea-review.json) includes pseudocode and full byte
reads of the audit and formatter entries, checked against pinned raw firmware.
The normal final build compiles 839 units (757 application and 82 bootloader),
with 75 application imports and 22 bootloader linker imports. One hardware
import closes without adding imports. All 834 prior nongenerated objects
outside the two changed units are unchanged; inside those units only the two
formatter entry code sections and retained-log worker code change.

The R1 manifest check passes. Global `make sources-check` still reports the
pre-existing unlisted G2 `resident_rom_thumb_set.S`. Cold initializer checks do
not prove final placement; final linking, physical timing and device boot remain
unverified. Byte identity is not required.
