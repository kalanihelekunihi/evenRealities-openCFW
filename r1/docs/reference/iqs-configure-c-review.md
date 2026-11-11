# C IQS controller configuration

`r1/src/application/board/native_iqs_configure.c` implements configuration at
`0x2f880` and table selection at `0x728b4`. The reset/recovery path now reaches
this C register setup through the existing IQS transport. Product-SN decoding,
slider calibration and the persisted compensation-word accessor remain explicit
unresolved dependencies; no lower operation is replaced by a success stub.

Configuration decodes the product SN, publishes the selected model record,
calibrates, then reloads the configuration pointer. It captures the model choice
and persisted compensation word. Only full-word values 1..31 override the
configuration's first byte. Logging reloads the mode and configuration halfword
at native sink boundaries. Setup issues these ordered writes, ignoring port
statuses and continuing:

| Register | Bytes |
| --- | ---: |
| 0x1f | 4 |
| 0x21 | 14 |
| 0x28 | 22 |
| 0x36 | 22 |
| 0x41 | 20 |
| 0x4b | 22 |
| 0x56 | 14 |
| 0x5d | 30 |
| 0x6c | 33 |
| 0x33 | 6 |

The two ten-entry model tables at `0x20007760` and `0x20007788` refer to twenty
aligned 30-byte register-data records. Every record matches stock ROM, including
padding; every C pointer relocation matches the authenticated cold RW mapping.
The configuration pointer at `0x20007738` starts null. These are data owners,
not retained executable code. Selector indexing preserves low-byte decoded-6;
the probes cover valid decoded values 6..15 and equivalent wrapped input words.
They do not establish safety for other indices or final startup placement.

The [machine-readable receipt](iqs-configure-c-review.json) records 1,644 direct
stock/C comparisons and 806 actual-port/transport/registry comparisons. Coverage
includes all twenty configurations, persisted divider boundaries and full-word
rejection, all byte values in a redirected mutable configuration, model changes,
changing logging modes, live pointer/table changes, and reads at each transfer
boundary. Callee saves, stack guards, PRIMASK and BASEPRI are checked. Twelve
compiled defects are rejected, followed by unmodified production-object reruns.

A further 612 comparisons and twelve defined private-buffer fallback checks
enter through the actual C IRQ, reset/recovery, configuration, model, averaging,
event and port/registry path. Kernel/device callbacks and the remaining lower
helpers are modeled. The [REA review](iqs-configure-rea-review.json) includes
configuration pseudocode and complete byte reads checked against pinned stock.
The 1,274-byte configuration body has an intervening 78-byte literal/string
island, so its complete entry span is 1,352 bytes.

A replay diagnostic observed modeled callback PC redirection falling through
under Unicorn after a conditional instruction. The passing harness uses an
explicit Cortex-M4 CPU and real Thumb callback return instructions; that repair
did not change firmware C. It is an emulator observation, not a device claim.

The normal reviewed build compiles 837 units (755 application, 82 bootloader),
with 79 application imports and 22 bootloader linker imports. All 834 prior
nongenerated objects are unchanged. The configuration import closes and exposes
three lower hardware/storage helpers. The R1 manifest check passes; global
`make sources-check` still reports the pre-existing unlisted G2
`resident_rom_thumb_set.S`. Final linking, physical timing and device boot
remain unverified. Byte identity is not required.
