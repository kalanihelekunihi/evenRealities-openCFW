# R1 HRV signaling comparison in C

Follow-up: the [conversion review](hrv-conversion-c-review.md) removes the remaining
producer assembly. The limits below describe this preceding comparison stage.

The HRV producer at stock `0x4a24c` now expresses its positive-result comparison
as `value > 0.0f`. GCC 9 with `-fsignaling-nans -frounding-math -ftrapping-math
-ffp-contract=off` emits signaling `VCMPE` against zero and transfers its condition
flags. This preserves the quiet-NaN invalid-operation flag that the earlier
Clang C comparison lost. The existing producer unit uses GCC profile 53; no new
function implementation, state owner or import is added.

The [receipt](hrv-positive-c-review.json) binds current source/object hashes,
the raw-image-checked REA evidence and verification artifacts. The complete
callback passes **4,608 paired stock/C cases**, including **16 expected faults**.
Checks cover signed zeros, finite values, infinity, quiet/signaling NaNs,
denormals, FZ/DN/rounding settings, FPSCR, live buffer aliases and provider state
mutations. Actual C timing teardown, buffer clear and timer coordinator execute;
RMSSD, wear, time, event/log providers and lower timer operations remain modeled.
Ten compiled defects are rejected, including a deliberately quiet comparison
using `__builtin_isgreater`. Compilation failures do not count as rejections.

All **672 units** compile and both relocatable compositions pass without duplicate
strong symbols. The other **671 source/object pairs** and both import sets remain
unchanged: **163 application / 34 bootloader** unresolved symbols. Qualification
rejects the producer's anchored relocation pattern, so no instruction-qualified
bytes are added. The canonical plan remains at **4,369 source-built bytes**; the
fresh hybrid matches the locked application through executable pull-through.

One inline assembly boundary remains in this producer: unsigned float conversion
with native saturation and exception behavior for infinity/overflow. A direct C
cast does not establish that behavior. This review proves neither first-use FP
activation, physical HRV operation, a complete source-only firmware link nor
byte identity for the new producer object.
