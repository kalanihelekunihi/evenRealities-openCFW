# C slider velocity and release-sequence helpers

`native_touch_slider_support.c` supplies the leaves at stock `0x59aac` and
`0x92c70`, reusing the existing contact buffer and client flags. It adds no state.
The [C state-machine review](slider-state-c-review.md) now records their
integration through stock `0x92cbc` and the IQS event callback.

The velocity filter keeps three coordinate/timestamp samples. It preserves the
three-unit direction dead band, reversal reset, rounded unsigned speed division,
255 cap and integer 40/60 smoothing. Zero elapsed returns the prior speed or one.
The ring index must be 0..2, as in stock; corrupt-index memory faults are excluded.
The release check uses the caller-owned timestamp, a 2,500-unit inclusive window,
byte-wrapped count and fifth-release trigger. It does not update the timestamp.

The [review receipt](slider-support-c-review.json) records 21,398 stock/C
comparisons over coordinate deltas, direction history, rounding, saturation,
time wrap, client flags, release thresholds and repeated sample sequences.
Nine compiled defects are rejected, followed by 17,558 unmodified comparisons.
All contact bytes, return words, callee saves, stack guards and interrupt masks
are checked. These leaves call no modeled services. REA byte reads match the
pinned stock body and literal pointers; the behavior was decoded from Thumb.
The active REA inventory does not contain the main slider function, so its failed
instruction request is not treated as decompiled evidence.

The normal build compiles 841 units (759 application and 82 bootloader), with
73 application imports and 22 bootloader linker imports. All 838 other prior objects are unchanged, including eight generated
application objects. The R1 manifest check passes; the global
check still fails on the pre-existing G2 `resident_rom_thumb_set.S` entry.
Final linking, runtime placement, physical sensing and device boot remain
unverified. Byte identity is not required.
