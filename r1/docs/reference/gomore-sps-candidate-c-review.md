# R1 accelerometer SPS candidate in C, 2026-11-10

Stock application `0x5ef1c` updates an 88-byte SPS candidate state from six
accelerometer features, the three-byte motion selector, and a float height
pointer. The source binding is
`r1/src/application/runtime/native_gomore_sps_candidate.c`. Its providers
replace stock model calls `0x68de0`, `0x68e5c`, `0x69e94`, `0x69f3c`,
`0x6773c`, and `0x484a8` with C arithmetic and the source-owned numeric
coefficients. The shared updater remains in
`r1/src/vendor/gomore_primitives/gomore_primitives.c`.

Paired Cortex-M4 execution compared the complete 88-byte state, eight output
bytes, and return word of stock and source-linked C. The ignored probe at
`build/r1-sps-candidate-20261110/` passed 144 controlled cases and 1,200
deterministic varied cases. These covered both model selections, calibration
flags, raw and smoothed motion states, cadence gates, height and feature
ranges, cooldown, cached values, and elapsed counts from zero through fifteen.
The probe's candidate and shared updater objects have the same SHA-256 hashes
as their current manifest Clang objects. This establishes the compared paths,
not all possible inputs or hardware behavior.

The comparison exposed two errors in the earlier generic C updater. Stock
model `0x69e94` scales the affine result by `values[0]/60` and then multiplies
by `3.6` after conversion to double. The fourth feature is `-1.0` in the
state-two path because the stock stack record shares that initialized word.
For a non-locomotion raw state that passes the cadence gate, stock also clears
both cached model outputs. Those three details are now reflected in C.

`./make.sh sources-check` reports 979 R1 units and no unbuilt sources. The
source build compiles and composes all 897 application and 82 bootloader units
without duplicate strong symbols; the strict bootloader link passes. The
strict application link remains incomplete with 21 undefined functions and
uses 618,240 of 696,320 available flash bytes. Receipts are under
`build/sources-r1-sps-candidate-c-20261110/`. No application boot or physical
sensor result is claimed.
