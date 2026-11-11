# R1 SpO2 timing sample callback native contract

The [receipt](spo2-sample-native-analysis.json) binds REA bytes, locked
artifact/ELF hashes and **13,152 native callback cases: 13,104 completed and
48 expected payload faults**. Another **512 native helper calls** exhaust the
unsigned-byte predicate/calibration domain. The 252-byte callback `0x4ada0`
remains unresolved; no firmware source or source plan changed in this analysis.

The callback retains incoming R0 as the stream handle, uses payload R1 and
ignores length R2. Raw logging reads all six payload bytes afresh for each
enabled log path. The native load order is **2,5,4,signed 3,1,0**; byte 3 is
sign-extended for the level argument. Validation happens **after raw logging**
and accepts byte 0 in inclusive range 70–100. That result is captured before
the wear predicate.

Only captured validation plus a nonzero wear predicate permits publication.
Calibration reloads byte 0 **after wear**, so providers can change the value
between validation and calibration. Conversion-result logs reload the raw
byte again but retain the calibrated byte. The eight-byte kind-**8** event is
the calibrated byte followed by **seven zeros**, with no timestamp. Publish
return failures are ignored.

The byte-domain calibration is `delta = value - 96`; multiply negative delta
by 5 and nonnegative delta by 8, divide by 10 with truncation toward zero,
add 96, then clamp to 70–100. Normal accepted input 70–100 maps to 83–99;
post-validation mutations can use any byte and still clamp to 70–100. The
existing C `gomore_primitives_piecewise_clamp_70_100` has the same formula in
this domain. A later [64-bit division review](eabi-divmod-register-return-review.md)
corrected its 32-bit wrapping and signed-16 narrowing outside the byte domain,
then passed 920 paired stock/C int32 inputs. The existing
`gomore_primitives_byte_in_70_100` takes a scalar byte, whereas the native leaf
takes a pointer. A C caller must perform a fresh volatile byte load at that
boundary. Reusing these helpers avoids adding duplicate implementations.
These are source inspection/domain findings, not compiled-helper equivalence
claims from this native-only fixture.

Cleanup runs even after invalid input or a failed wear predicate. It
**unconditionally unregisters the incoming handle** with `spo2`, including zero,
then clears timing slot 1 late. The shared timer-release coordinator reads its
timer fresh and clears it after the lower release returns. Finally, captured
validation selects **flag byte 1 = 1 when valid, else flag byte 2 = 1**. That
choice does not depend on wear or publication. The other flag is preserved,
including provider changes. A release provider can repopulate an earlier stream
slot; there is no final blanket clear. The stream framework's void dispatch
at `native_stream_dispatch.c` discards callback return values.

The corrected mutation driver has 768 configured cases, **528 with the chosen
provider actually reached**. They exercise payload/state changes during mode,
raw/conversion logging, wear, publish, unregister and timer release. Saved
integer/FP registers, SP, masks, FPSCR, public writes and state are checked.
Native predicate, calibration and timer-release coordinator instructions execute;
other providers are modeled. The full corpus was rerun after fixing the driver
to use provider names rather than numeric addresses.

Null and `0xffffffff` payloads fault before cleanup. With raw ring logging
enabled the first read is payload+2; with logging off validation first reads
payload+0. Fault address and byte width are recorded. Cases also cover every
raw byte value, signed level boundaries, invalid length, shared-storage aliases,
incoming handles zero/`0xffffffff`, provider failures and timer changes.
All 663 current source/object hashes and the manifest remain unchanged. Only
the existing unresolved frontier row gains this evidence receipt. Compiled C
callback/helper equivalence, physical providers, concurrency and final
source-only linking remain unproven.

The subsequent [C review](spo2-sample-c-review.md) implements this contract
and compares the production callback and existing C helpers with stock.
