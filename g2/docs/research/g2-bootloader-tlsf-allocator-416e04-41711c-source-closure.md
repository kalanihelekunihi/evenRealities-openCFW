# G2 bootloader TLSF allocator-operation source closure

The ten complete authenticated entries at `[0x00416E04,0x0041711C)` now route
to compilable freestanding C in
`components/bootloader/core_overlay/runtime_tlsf_allocator_416e04.c`. The
16,581-byte source hashes to
`a1333a05d1c4fe6b18d51d8c893d1af709c5358541bad49efee57385fd985587`
and is a bounded BSD-3-Clause adaptation of Matthew Conte TLSF v3.1 for the
recovered G2 ILP32 layout.

The 792 authenticated stock bytes cover request-size adjustment, free-block
capability, split, leading and trailing trim, absorb, previous/next coalescing,
free-block lookup, and used-block preparation. Apple clang emits 748 Thumb
bytes under 58 strict relocations. Host tests exercise boundary adjustment,
minimum remainders, pointer/link rewrites, bitmap/list transitions,
coalescing combinations, exhaustion, and allocation preparation. A
freestanding Cortex-M55 compile gate pins the 16-byte header and recovered
control layout.

The complete offline overlay, provider, manifest, package, flash-plan, and
dual-profile gates pass as part of `make bootloader-numeric-closure`. No image
was signed, flashed, installed, reset, or booted. Live fragmentation,
coalescing, allocator-caller, and boot evidence is blocked because no
authorized responsive G2 right temple is available. This bounded tranche is
software-closed; firmware-wide functional completeness is not claimed.
