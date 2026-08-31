# G2 LVGL/Nema target-runtime provider source admission

Status date: 2026-08-30  
Scope: memory and ARM EABI conversion imports retained by the Ambiq/Nema
relocatable link  
Mode: bounded source semantics, exact hard-float/base-PCS ABI probes, hostile
host tests, and deterministic Cortex-M55 link audit; no production routing,
firmware-image integration, MMIO, flashing, or hardware operation

## Result

The next independently closable zero-import tranche supplies five exact target
runtime symbols:

- `memcpy` and `memset`;
- the aligned-copy ABI entry `__aeabi_memcpy4`;
- binary64-to-signed-64 `__aeabi_d2lz`; and
- binary32-to-unsigned-64 `__aeabi_f2ulz`.

The checked consumer graph contains 21 retained relocations: one backend call
to `__aeabi_memcpy4` and 20 authenticated public Nema archive relocations to
the other four APIs. All owning objects and counts are recorded under
`local_target_runtime_provider.closed_consumer_relocations`.

This moves the maximal residual from 45 to 40 symbols. Its canonical sorted
digest is
`e64fd7fd6ec347f0253daee5236ba980445f568815ffbe0fed40774db5d08f5e`.
With the exact scoped AmbiqSuite and Apollo510-EVB inputs, the maximal partial
is 1,575,872 bytes with SHA-256
`cfcf1749b327ba5698830a2d8a3056aacd2e1987915caf44c932e8c9c868054c`.
This is an isolated source/link result, not production routing.

## Selection and dependencies

These five APIs are the largest remaining dependency-closed set found that
needs no allocator, LVGL state, scheduler, OSAL, C library, libm, compiler
runtime, fixed address, or hardware. The memory algorithms reuse the already
reviewed component-local scalar-runtime behavior. The conversion algorithms
use direct IEEE-754 sign/exponent/significand decomposition and do not perform
floating-point arithmetic in their target bodies.

The ten FreeRTOS OSAL imports remain excluded because the exact
`LV_USE_FREERTOS_TASK_NOTIFY` choice and its task/semaphore/scheduler ABI are
not recovered. `utf8_codepoint_size` also remains excluded: the private GPU
patch proves its one-to-four-byte result domain but not the exact malformed
UTF-8 classification policy. Supplying either policy by preference would not
be evidence-based.

## Algorithm and ABI evidence

Conversion semantics are bounded against the official LLVM compiler-rt tag
`llvmorg-20.1.8`, commit
`87f0227cb60147a26a1eeb4fb06e3b505e9c7261`, under
`Apache-2.0 WITH LLVM-exception`. The manifest records byte count, Git blob
SHA-1, and SHA-256 for `fixdfdi.c`, `fixunssfdi.c`, `fp_fixint_impl.inc`, and
`fp_fixuint_impl.inc`. This is an algorithmic source ceiling; the local MIT
provider is an independently bounded implementation and does not claim textual
identity with compiler-rt.

The target provider compiles for `arm-none-eabi`, Cortex-M55, Thumb, hard
float, short enums, freestanding GNU C11, `-fno-builtin`, function/data
sections, and all warnings as errors. The source object is 2,308 bytes with
SHA-256
`2a43b8130fe85d3e2b27e25efa386ac92f466fb83de85c6f6c083b9643a92a88`.

The 1,648-byte ABI probe has SHA-256
`918bd5ffff80d2240c8924c7b299f80a286d1c13002a656a5a9acb670c805c4b`.
It asserts four-byte pointers/`size_t`, IEEE binary32/binary64 widths, and
64-bit integer widths. Its exact instructions marshal a default hard-float
caller's binary64 argument from `d0` into `r0/r1` and binary32 from `s0` into
`r0`, followed by one `R_ARM_THM_JUMP24` to each base-PCS AEABI conversion.

`ld.lld -r --gc-sections` retains exactly the five exports in a 2,736-byte
object with SHA-256
`c009f816e4d59547783e88272d77bf9fccaf765f5d66d6339fc3296ca4256bf7`.
The object has zero undefined symbols, zero external relocations, and zero
fixed-address imports.

## Hostile and defined-domain behavior

For the C/AEABI defined domain:

- memory copies/fills preserve byte order, length, return values, and the
  aligned-copy entry's void ABI;
- finite representable conversions truncate toward zero;
- negative inputs to the unsigned conversion return zero; and
- signed/unsigned range endpoints preserve all representable 64-bit results.

Undefined or exceptional inputs are deliberately bounded: zero-length memory
operations accept null, other null memory inputs do not dereference, signed
overflow/infinity/NaN saturates according to the encoded sign, and positive
unsigned overflow/infinity/NaN saturates to `UINT64_MAX` while negative
encodings return zero.

The host oracle verifies ordinary, unaligned, aligned, zero-length, and null
memory cases; conversion boundaries around zero, 32-bit and 64-bit powers,
signed endpoints, infinities, and both NaN signs; and 10,000 deterministic
binary64 plus 10,000 binary32 encodings against native casts whenever the cast
is defined. AddressSanitizer and UndefinedBehaviorSanitizer remain clean.

## Reproduction and remaining boundary

From `g2`:

```sh
python3 tools/audit_g2_lvgl_nema_link.py \
  --write-manifest tools/manifests/g2-lvgl-nema-link-admission.json
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_target_runtime_provider
python3 -m unittest -v tests.test_audit_g2_lvgl_nema_link
```

The provider is not registered in the Apollo core overlay. Production use
still requires collision and ownership review against the selected C library,
compiler runtime, and the existing IMU-local `__aeabi_memcpy4` definition.
The remaining 40-symbol link boundary contains libm, LVGL allocator/global/
draw/decoder/font/vector/OSAL APIs, and the private UTF-8 helper.

A subsequent independently admitted five-symbol musl math provider moves the
current residual to 35; see `g2-lvgl-math-provider-source-admission.md`. The
40-symbol count and maximal-partial identity above remain the historical result
at this target-runtime tranche.

No authorized physical target identity, transport, GPU trace, framebuffer
capture, or display observation was supplied. These scalar functions need no
live hardware for isolated C/ABI closure; complete Apollo510/Nema behavior
remains blocked on unavailable physical evidence.
