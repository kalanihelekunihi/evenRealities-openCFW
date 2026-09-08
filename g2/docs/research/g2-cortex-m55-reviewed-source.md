# Reviewed Cortex-M55 C replacements

Date: 2026-09-07. Build target: Apple Clang on this macOS host.

Four bounded functions are reconstructed as C using the existing unmodified
Arm CMSIS header at commit `d23a6949a0331ca96853bcd98b0fdcc4db47184c`.
The source uses `__DMB`, `__get_IPSR`, and `__get_PSP`; CMSIS retains its
Apache-2.0 notice and license. The small adapters are MIT. This is reuse of
reviewed upstream processor intrinsics, not an assertion that CMSIS generated
the original firmware.

| Stock range | Recovered behavior | Compiled bytes |
| --- | --- | ---: |
| `0x004488EC..0x004488F4` | Store 32-bit word, then full-system DMB | 8 |
| `0x004488F4..0x004488FC` | Load 32-bit word, then full-system DMB | 8 |
| `0x00442228..0x00442238` | Test the complete IPSR value for nonzero | 12 |
| `0x005939A0..0x005939A6` | Return the process stack pointer register | 6 |

The atomic store, atomic load, and PSP functions compile byte-identically to
their stock bodies. The exception predicate uses an equivalent shorter
sequence within its 16-byte envelope. These sources do not include extracted
instruction bytes, pointer literals from the firmware, or external runtime
imports.

## Why decompiler helpers alone are insufficient

The harvested `FUN_004488f4` calls `DataMemoryBarrier(0x1f)` before evaluating
`*param_1`, but the actual instructions are `ldr r0, [r0]`, `dmb sy`, and
`bx lr`. Substituting a valid DMB helper would compile the wrong ordering.
The reviewed C captures the volatile load before invoking CMSIS's memory
barrier.

The harvested `FUN_00442228` tests only `getCurrentExceptionNumber() & 0x1f`
after a synthetic privilege check. The stock code reads IPSR directly and
compares its complete value with zero. Truncation would misclassify nonzero
exception numbers such as 32, 64, and 256. The reviewed source preserves the
actual register test.

The installed Ghidra 12.1.3 ARM SLEIGH definitions confirm that these names
are processor operations, including the misleading `enableIRQinterrupts(x)`
name for a PRIMASK write and a five-bit DMB operand token. Those definitions
are useful evidence, not replacements for the authenticated instructions.
Other processor and register artifacts remain unresolved rather than receiving
invented behavior.

## Admission and checks

`tools/transparent/reviewed_sources.json` pins each stock interval, source
file, upstream header/license, and compiled text. Generation authenticates the
firmware and all review inputs before writing output. Reviewed C supersedes
the corresponding decompilation, which remains separately available under
`decompiled-evidence/`. Compilation or placement drift is a build error;
reviewed functions cannot silently degrade to traps.

The image report counts reviewed code separately. Compilation of unreviewed
functions no longer satisfies the source-readiness check even when it fits
and contains no traps. This prevents future progress from confusing syntactic
recovery with behavior recovery.

Focused tests verify atomic load/store ordering with a CMSIS host model,
all 512 possible IPSR exception values, PSP values, the three exact target
instruction sequences, all four compiled-text contracts, and rejection of
changed source, upstream dependencies, firmware, boundaries, and image text.
They also reject a syntactically complete but unreviewed image at the readiness
gate. No physical operation is performed.

```sh
make -C g2 transparent-test
make -C g2 transparent-image TRANSPARENT_BUILD_DIR=build/transparent-reviewed-cortex-m55
```

The complete macOS image build succeeds with 5,149 placed functions. Four
use the admitted C above, producing 34 bytes in 38 stock bytes of envelopes;
the other 5,145 still use unreviewed decompilation. Total compiled code is
711,178 bytes, padding 194,974, vendor-derived data 2,128,548, and traps
488,696. The image SHA-256 is
`8483db1df18d1c4f989c5fb008057bb63c330ef8cb1df7dd55da29a654ac4998`.
All 35 reconstruction tests pass.

These are reviewed replacements in the experimental Apollo image, not a
claim of complete firmware recovery or production hardware qualification.
The existing hybrid package is not modified by this source-admission path.
