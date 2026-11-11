# C slider state machine and typed IQS callback

`native_touch_slider.c` implements stock `0x92cbc`. The touch worker now includes
its typed callback declaration: four words in R0..R3 and a binary32 pressure in
S0. Existing contact, calibration, timer, synthetic-release, client and gesture
owners are reused. Seven remaining context fields have narrow owners whose
compiled initializers match the authenticated expanded RW image.

The implementation preserves coordinate normalization and observed bounds,
pending-tap cancellation, press/slide/long-press transitions, release sequencing,
unsigned time wrap and the separate synthetic release record. It keeps the
50/15-unit movement gates, 100-unit spacing, 150-unit early pressure gate,
300-unit pending window and strict interior margins. Held samples below the
movement/long-press gates dispatch an empty record. Failed first-movement timing
or pressure gates return after updating the mode, without dispatching a record.

Binary32 contraction is disabled. The native signed float-bit pressure comparisons
and unordered-scale path are explicit, with defined VFP-compatible unsigned
conversion. Existing logging providers are used with typed declarations.

The [review receipt](slider-state-c-review.json) records 10,482 direct stock/C
comparisons and 8,498 comparisons with actual C gesture handling. Another 756
comparisons enter through the actual C IQS normalized-float event frontend and
registered callback, checking all four integer arguments and S0 at the slider
entry. Velocity, release sequence, gesture and standard memory routines execute
as C. Thresholds, non-finite values, every interior-coordinate byte, timer state,
provider mutations and repeated sequences are covered. Sixteen compiled defects
are rejected; final normal-object verification passes after those controls.
The final declaration-only correction retains identical object bytes to the
fully verified build, with an additional callback-route rerun.

REA bytes match the pinned stock span, including its literal island and the
following event-pointer/pressure-limit literals. The function
is absent from the active REA analyzed-function inventory, so the unsuccessful
decompiler/instruction requests are not treated as pseudocode evidence. The
behavior contract comes from the three authenticated Thumb instruction ranges
and native/C execution comparisons.

The normal build compiles 842 units (760 application and 82 bootloader), with
72 application imports and 22 bootloader linker imports. The slider import closes
without adding imports. All 831 prior nongenerated objects remain unchanged;
the typed worker include also preserves its object bytes. The R1 manifest check
passes. Global `make sources-check` still reports the pre-existing unlisted G2
`resident_rom_thumb_set.S`.

The IQS integration starts after channel samples become a float; it does not
exercise I2C transfers or the complete IRQ worker. Lower clock, logging, model,
scheduler, connection and BLE services are models. An ordinary void callback ABI
is tested; private native frame addresses and incidental caller-clobbered values
are excluded. The velocity ring index must remain 0..2. Final linking, runtime
placement, physical timing and device boot remain unverified. Byte identity and
a paid compiler are not required.
