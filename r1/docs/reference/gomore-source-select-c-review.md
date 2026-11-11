# R1 GoMore source selection in C, 2026-11-10

The locked R1 application `r1-2.2.6.0009/application.bin` has SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Its GoMore selectors at `0x605dc` and `0x610c8` now have native ABI C
adapters in `r1/src/application/runtime/native_gomore_select_hr.c` and
`native_gomore_select_sps.c`. They call the existing source-owned selection
primitives; the heart-rate primitive's direct-path quality word was corrected
from integer `1` to the stock float bits for `1.0f` (`0x3f800000`). The
SPS primitive required no change.

The stock heart-rate entry receives state, an unused elapsed count, direct
and estimated float-field addresses, then an output address. It logs the
float values as doubles, selects direct only when encoded bits represent
40..240 and the state byte is zero, then falls back to estimated in that
range. The direct quality is `1.0f`; estimated quality is copied as raw bits;
an invalid result has source `0x40`. The stock SPS entry logs three float
field pointers, chooses the first nonnegative reference/GPD/accelerometer
value, writes its source index and `3600.0f / value` when positive, and
always copies the accelerometer auxiliary byte. Unordered NaNs fail the
nonnegative test, as checked in the stock emulator. Its return is the source
index or `0x40`.

An ignored Unicorn ARM Cortex-M4 probe under
`build/r1-hr-selection-probe-20261110/` linked the actual compiled C units
and ran them against the locked stock bytes, intercepting only the configured
logger. It compared complete output bytes, return values, logger format and
arguments for 590 heart-rate and 1,241 SPS cases, including boundary floats,
negative zero, infinities, NaNs and randomized bit patterns. All 1,831 paired
cases matched. The probe receipts are `result.json` and `result-sps.json`.

The final four-stage manifest build is
`build/r1-gomore-four-stages-c-20261110/report.json`: 956/956 R1 units
compile, with no duplicate strong definitions. Its strict bootloader link
passes. The strict application receipt at
`build/r1-gomore-four-stages-c-20261110/app-link/report.json` has 46
unresolved references and a 28,040-byte full flash overflow. Compilation and
these bounded function comparisons do not establish complete application
linkage, board behavior, or byte identity. The adjacent step and activity
entries are reviewed in [GoMore accumulators](gomore-accumulators-c-review.md).
