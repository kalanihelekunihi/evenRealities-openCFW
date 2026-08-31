# G2 LVGL/Nema FPv5-D16 math provider source admission

Status date: 2026-08-30  
Scope: `cosf`, `sinf`, binary64 `sqrt`, and `tanf` in the authenticated atomic link  
Mode: exact upstream source, deterministic Cortex-M55 ABI/relocation audit,
full-range reference tests, and hostile host gates; no production routing,
firmware integration, flashing, MMIO, or hardware operation

## Result

An isolated provider closes the four remaining scalar math imports and moves
the canonical maximal residual from 31 to 27 symbols. The new digest is
`ea3aeb3c448fe6ca813d842d6d87b1a590bf04e45cfd13d13159669d9e0657d7`.
The exact scoped maximal partial link is 1,597,056 bytes with SHA-256
`c6fd16a4fdd11c19ea050668ee85bc96c09cae7b685e7824518897db702f3e23`.

The provider is 13,144 bytes with SHA-256
`3b67eea354a8f12f48faed3177b9d170fa7c8191ced9e30803cbe6b31b2e8c8a`.
It exports exactly `cosf`, `sinf`, `sqrt`, and `tanf`; it has no undefined ELF
symbol, external relocation, fixed address, allocator, scheduler, libc, or
libm dependency. Thirty-five authenticated consumer relocations are closed:
34 in selected NemaVG archive members and one binary64 `sqrt` call in
`lv_draw_ambiq_vector.o`.

This is source and relocatable-link admission only. The provider is not
registered in the Apollo production overlay.

## Authenticated source closure

The analyzer pins 14 exact musl Git blobs at tag `v1.2.5`, commit
`0784374d561435f7c787a555aeab8ede699ed298`: the four public algorithms,
three trigonometric kernels, float and large argument reduction, `floor`,
`scalbn`, the square-root reciprocal table and declaration, and the invalid
domain helper. The trigonometric and reduction files retain their Sun
permission notices; the remaining files and compatibility surface are
covered by musl's MIT terms.

The component-local `math.h`, `libm.h`, and `features.h` supply only required
types, declarations, visibility, bit casts, and floating evaluation helpers.
All upstream algorithm files remain byte-exact and are verified by Git blob
identity before compilation. Hidden symbols are renamed only through compiler
definitions and localized after the relocatable link.

## Target and numerical boundary

Every source is compiled for Arm-none-EABI Cortex-M55, Thumb, hard-float,
`fpv5-d16`, short enums, freestanding GNU C11, hidden internal visibility,
function/data sections, `-fno-builtin`, and all warnings as errors. Apollo
stock-source evidence independently contains FPv5-D16 binary64 instructions,
so the build is not based solely on a CPU-name guess. The result does not
establish live CPACR/FPU enablement, context preservation, FPSCR state, or
rounding mode.

The 2,240-byte ABI probe has SHA-256
`c7122f705fa35d40f468d4bbc9e68c56746fc6da089639e7526a639add3bf354`.
It asserts binary32/binary64 widths and emits exactly one
`R_ARM_THM_JUMP24` relocation to each public API.

The deterministic host oracle exercises 10,000 arbitrary binary32 bit
patterns across each trigonometric function and 10,000 positive binary64
values spanning normal and subnormal exponents. Results are compared to the
native/Python reference within one ULP. The ASan/UBSan fixture separately
covers signed zero, infinities, NaNs, negative square-root inputs, and exact
finite roots.

No `errno`, signaling-NaN payload, or floating-exception equivalence is
claimed. Production symbol collision, optional-DP FPU runtime state, and
physical rendering remain explicit blockers.

## Reproduction

From `g2`:

```sh
python3 tools/audit_g2_lvgl_nema_link.py \
  --write-manifest tools/manifests/g2-lvgl-nema-link-admission.json
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_math_dp_provider
python3 -m unittest -v tests.test_audit_g2_lvgl_nema_link
```

No authorized physical target identity, transport, FPU-status capture, GPU
trace, framebuffer capture, or display observation was supplied. Hardware
behavior and complete rendering remain blocked by unavailable physical
evidence.
