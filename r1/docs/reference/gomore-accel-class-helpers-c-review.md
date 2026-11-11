# R1 accelerometer classifier leaves in C

`native_gomore_accel_class_helpers.c` implements three lower contracts of the
still-unresolved classifier at `0x67e4c`:

- `0x56980` reads exactly eight signed halfwords, sums nonzero values and
  divides by their count under the live FP mode. All-zero input returns +0.
- `0x7eaf6` counts unsigned-halfword rising crossings above 1,200, rearms only
  below 1,000 and wraps its count to eight bits. Equality at either threshold
  stays in the deadband. Count is interpreted as signed 32-bit; nonpositive
  counts perform no reads.
- `0x56920` converts the raw signed R0 integer to float and evaluates the four
  fixed weighted terms plus bias with the native non-fused operation order.
  Its signaling comparison returns 1 only for a negative ordered result;
  nonnegative and unordered/NaN results return `0xffffffff`. This differs from
  a plain ordered C `>= 0` implementation.

The coefficient words at `0xbd26c` are `be445123`, `3f697fe1`, `bc00b405`,
`3f7237e0`; bias at `0x5697c` is `bf4485ee`. They are represented as typed
float bit constants, verified against the locked application. No executable
opcode array or retained executable body is added to the C source. The GCC9
strict FP profile and separate arithmetic/comparison calls preserve the tested
rounding, signaling and non-fused behavior.

Verification passes:

- 43,808 direct native/C pairs: 2,096 nonzero-mean, 1,168 hysteresis and 40,544
  linear-classifier cases, including 39 logical faults. Coverage includes every
  nonzero-slot mask, byte-counter wrap, strict threshold equality, signed counts,
  pointer alignment, nonfinite/subnormal FP classes, integer conversion limits,
  live FPSCR flags/modes and near-decision-boundary inputs.
- 5,816 actual accelerometer-stage pairs through C preprocessing/collector/math
  and the stock classifier. This matrix exercises the new mean 8,859 times;
  crossings and linear decision remain unvisited in that matrix.
- A separate 216-pair classifier replay seeds suitable history and periodic,
  square/ramp/zero waveforms. It exercises the C mean 864 times, crossings 216
  times and linear decision 162 times. All entry depths, arguments, public
  buffers/writes, results and FPSCR match. The remaining classifier/spectral
  code stays stock. REA identifies this classifier as each helper's observed
  direct caller; unresolved indirect uses remain outside that inventory proof.
- 864 checked-interface pairs and five guard cases. Checked mean/crossing APIs
  delegate to the shared native C implementations. The general linear utility
  keeps its injected coefficient/bias API and is explicitly named `_checked`.
- Twelve rejected defects: divide-by-eight, seven-slot mean, inclusive high/low
  thresholds, missing byte wrap, unsigned length, ordered NaN decision, one-ULP
  bias change, fused multiply-add, unsigned conversion, wrong coefficient sign
  and omitted integer term.

Tests compare raw S0 or integer results, full input hashes, ordered public
writes, FPSCR, preserved registers, SP and masks. Helper entry depths remain
compared; private save bytes/unexposed internal C frames and caller-clobbered
register/APSR residue are excluded. Fault tests compare logical access/width,
not complete exception frames or exact fault PCs. Physical and concurrent
sensor behavior remain unverified.

The fresh normal build compiles 712 units (638 application, 74 bootloader)
without failures or duplicate strong symbols. Imports remain 178/34; the
classifier root is still an explicit unresolved dependency. Manifest validation
passes. Exact qualification rejects all three bodies, so the canonical plan
stays at 4,381 source-built executable bytes, 641,779 stock executable bytes
and 248 resource bytes. The fresh R1 hybrid application matches stock. Full
source-only linking, C byte identity and source completeness remain unfinished.
The [machine receipt](gomore-accel-class-helpers-c-review.json) records REA,
source/object hashes, coverage counts and validation limits.
