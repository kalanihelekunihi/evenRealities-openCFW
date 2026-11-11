# C EABI conversion providers for sensor consumers

The normal application composition now supplies six previously unresolved Arm
runtime interfaces: __aeabi_d2f, __aeabi_f2d, __aeabi_l2f, __aeabi_ul2f,
__aeabi_ul2d and __aeabi_dcmpge. No precompiled runtime archive is linked.

`runtime/eabi_float_conversions.c` supplies typed base-PCS entry points around
three existing canonical bit-pattern providers: r1_log_double_to_float_bits,
r1_binary32_to_binary64_bits and r1_signed64_to_binary32_bits. The wrappers use
union bit views rather than numeric casts. This matters: the recovered stock
conversions lose zero signs and have non-IEEE handling of small/exotic exponent
encodings. Generic LLVM narrowing/extension providers were investigated but
are not selected. Existing private LLVM signed64 conversion names are retained;
there is no second canonical __aeabi_l2f implementation.

Two unmodified LLVM compiler-rt 20.1.8 C sources supply unsigned64-to-float and
unsigned64-to-double. Their exact source URLs/hashes and the existing license
are retained in the pinned source slice. The double conversion uses the already
composed C double-add provider. `runtime/eabi_double_compare.c` gives the
base-PCS Boolean ge interface over the existing LLVM ge comparator; unordered
inputs return false. This is the Boolean ABI needed by compiled C consumers,
not a replacement for the separate stock APSR flag-comparison interface.

## Executed verification

`build/goal-r1-eabi-conversions-c/verify.py` passes 32586 calls:

- 2060 double-to-float and 2060 float-to-double vectors compare the EABI entry
  against actual locked stock instructions, including zero signs, subnormal,
  exceptional and selected/random encodings.
- 2245 integer vectors test signed64 conversion against stock, and unsigned64
  conversion against an independent integer significand/remainder ties-to-even
  oracle for binary32 and binary64. Selected bit/rounding boundaries and random
  full-width values are included.
- 2192 double comparison pairs match independent Boolean comparisons, including
  NaNs, infinities and both zero signs.
- Compiled C caller probes exercise hard-float inputs/returns through the
  core-register EABI interfaces. Core and VFP callee-saved registers, SP and
  interrupt masks are checked. C execution is prohibited from entering the
  stock-code region; only explicit stock-oracle calls may execute there.
- The existing Goodix C source passes 120 signed64 mean and seven quantile
  interpolation cases. Its normal object has one monolithic text section, so
  the probe recompiles the unchanged source with function/data sections to
  isolate these routines from unrelated unfinished algorithms. This is C-source
  ABI integration evidence, not execution of the exact normal-build Goodix object
  or proof of the full biometric algorithms.

Five compiled defects—wrong PCS, wrong narrowing, changed zero sign,
signed/unsigned confusion and unordered comparison acceptance—are detected,
followed by a clean baseline. REA byte readbacks bind the three stock conversion
spans; their IDs/hashes are in the adjacent JSON receipt.

The tests use the default nearest-even floating environment. Exception flags,
nondefault rounding modes, timing and instruction identity are not claimed.
The LLVM fp_mode provider already in the build reports nearest-even and does
not raise a modeled inexact flag; this change does not alter that policy.

## Composition and remaining scope

`build/sources-goal-r1-eabi-conversions-final-c/report.json` compiles 784/784
units: 702 application and 82 bootloader, without failures or duplicate strong
symbols. Application imports fall from 120 to 114, removing exactly these six
names and adding none. The prior 778 object hashes match; two generated boot
objects differ in debug-path metadata but preserve allocated bytes/relocations.
Sensor consumers and the canonical stock bit-pattern providers are unchanged.
The strict GNU bootloader link still succeeds without undefined symbols.

R1 validation passes (784 units, 580 source files, zero excluded units). Global
sources-check retains the pre-existing unlisted G2 assembly-file failure. No
source-plan/qualification selection changes, opaque runtime blobs, firmware
publication or device writes are introduced. Full application linking and
physical sensor/firmware validation remain outstanding.
