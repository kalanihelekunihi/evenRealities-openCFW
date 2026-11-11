# R1 host-input adapter in C

`native_gomore_host_input.c` implements stock `0x94590` (260 bytes).
The [receipt](gomore-host-input-c-review.json) binds the REA bytes and pseudocode,
production object, replay, defect controls, caller audit and build reports.
It adds no inline assembly or persistent RAM owner.

The adapter preserves ordered packet reads, live context reloads after lower
providers, raw inactive-byte publication, count clamping, exact profile-two
checks, raw floating-point copies and wrapping index subtraction. All three
accelerometer input pointers are captured before output pointers are published.
Lower-provider return values are ignored and the adapter returns zero, as stock
does. Published scratch pointers retain the native automatic-storage lifetime.

The aligned C scratch structure is 420 bytes. The selected Clang `-Oz` profile
saves 20 bytes of registers and reserves 428 bytes, matching the native 448-byte
depth relative to this function's entry SP. Provider arguments and published
scratch pointers are compared as absolute numbers, without normalization.
Other compiler optimization profiles tested here used a different frame size.
The source manifest records the selected flags.

Direct native/C/independent-model replay passes **2,964 cases**, including
**11 fault cases**, and observes **8,859 modeled provider calls**. Coverage
includes payload/context overlap, provider mutations, live pointer replacement,
count/status extremes and selected floating-point bit patterns and FPSCR modes.
The fixture compares the defined 420-byte scratch view, metadata/context effects,
provider arguments, return, preserved registers and FPSCR. Eleven independently
compiled defective variants are rejected; compiler failures are not counted as
successful defect detection. The resampling and algorithm providers remain
modeled in this fixture. Emulator behavior does not prove physical alignment
traps or device execution.

A separate audit executes the actual sensor-update caller up to host entry.
Stock consumes 56 bytes in that caller; the current C caller consumes 64 bytes.
Both pass the same packet and index, but C host scratch addresses would therefore
be eight bytes lower from a common outer entry SP. This remains an explicit
integration boundary. Direct adapter equivalence relative to its own entry SP
is not whole-call-chain pointer equality. Compiler experiments did not resolve
that difference and no parent source was changed for this review.

The normal build compiles **679 units** (605 application, 74 bootloader), with
**167 application and 34 bootloader unresolved imports**. All 678 preceding
source/object pairs are unchanged. The host import is replaced by three lower
imports: ACC resampling `0x60990`, PPG resampling `0x60a14`, and algorithm output
`0x5ff94`. Source checks pass. Qualification selects no new source replacement;
the canonical source plan is unchanged. Hybrid raw equality still depends on
executable stock pull-through and does not establish a fully C firmware or
byte-identical source reconstruction.

Reproduction artifacts are under `build/goal-r1-gomore-host-input-c/`:
`verify.py`, `results.json`, `negative.py`, `negative-results.json`,
`caller-audit.py`, `caller-results.json` and `finalize.py`. The production build
report is `build/sources-goal-r1-gomore-host-input-c/report.json`.

The subsequent [resampler review](gomore-resample-c-review.md) supplies both
adapters in C and adds actual host/resampler replay. The algorithm remains
modeled there and the outer sensor-update frame mismatch remains open.
