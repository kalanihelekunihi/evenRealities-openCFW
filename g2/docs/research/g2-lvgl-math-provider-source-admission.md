# G2 LVGL/Nema scalar-math provider source admission

Status date: 2026-08-30  
Scope: five independently closable math imports in the Ambiq/Nema atomic link  
Mode: authenticated source, deterministic compatibility patch, host numerical
and hostile-input gates, Cortex-M55 ABI/relocation audit; no production routing,
firmware-image integration, flashing, MMIO, or hardware operation

## Result

An isolated component-local provider closes `acosf`, `atan2f`, `atanf`,
`fmod`, and `fmodf`. The authenticated consumer graph contains 46 retained
relocations: 44 from selected NemaGFX/NemaVG archive members and two `fmod`
calls from `lv_draw_ambiq_arc.o`. The maximal residual moves from 40 to 35
symbols. Its canonical sorted digest is
`44df8ce5b1415e0199f936181057d97c0aa96bb53da2e01cc840f4a2c599ae83`.

The final provider is 6,576 bytes with SHA-256
`123f1163b67fa953c3a77aa9ce3da7652fa6aae1001dc206b9f742f75f14a1af`.
It exports exactly the five admitted APIs and has no undefined ELF symbol,
external relocation, fixed address, allocator, scheduler, libc, or libm
dependency. With the exact scoped AmbiqSuite and Apollo510-EVB inputs, the
1,582,260-byte maximal partial link has SHA-256
`a09d0e19fd361b3653acde1711b42d612cff6950f85b7cef104173741af1fbf6`
and the same 35-symbol residual.

This is source and relocatable-link admission only. The provider is not
registered in an Apollo production overlay.

## Authenticated source and bounded patch

The five algorithm translation units and `COPYRIGHT` are byte-exact copies
from musl tag `v1.2.5`, commit
`0784374d561435f7c787a555aeab8ede699ed298`. The analyzer pins their byte
counts, SHA-256 values, and Git blob identities. The arc functions preserve
their original Sun permission notices; `fmod.c` and `fmodf.c` are covered by
musl's MIT terms.

Two component-local headers supply only the musl internal bit-cast,
floating-evaluation, and declaration surface needed by these files. A pinned
1,758-byte patch with SHA-256
`4de9dcfec25503530f0451fff8b2b95ed1980b4c4c526a783dad2b2a42ab3ecf`
is applied to temporary copies of `fmod.c` and `fmodf.c`. It replaces invalid
`(x*y)/(x*y)` paths, which pull unavailable binary64 runtime operations under
the G2 single-precision FPU ABI, with canonical quiet-NaN bit construction.
It also constructs signed zero by bits rather than floating multiplication.
Finite nonzero remainder loops are unchanged.

The deliberate invalid-input policy returns quiet NaN for a zero divisor,
NaN divisor, or infinite numerator and preserves the numerator sign for exact
zero remainders. It does not claim musl-compatible `errno`, `FE_INVALID`,
signaling-NaN payload, or floating-environment behavior.

## Target ABI and numerical gates

The analyzer compiles each source independently for `arm-none-eabi`,
Cortex-M55, Thumb, hard float, `fpv5-sp-d16`, short enums, freestanding GNU
C11, hidden internal visibility, `-fno-builtin`, function/data sections, and
all warnings as errors. `acosf` uses a component-local `VSQRT.F32` helper;
this proves instruction selection and link closure, not live FPU status or
rounding-mode behavior.

The 2,556-byte ABI probe has SHA-256
`6cf6b2cde6c8035b10faf35fac4a1e6ef2e9b134d617548a2659a671f5cc222e`.
It asserts four-byte pointers, binary32 floats, and binary64 doubles and emits
one `R_ARM_THM_JUMP24` relocation for each exact public prototype. The linked
object is post-processed only with `llvm-objcopy --localize-hidden`, leaving
the five public APIs and making every imported musl helper local.

The host gates compare 5,000 deterministic values per function family against
the native/Python mathematical reference within one ULP, including widely
distributed normal and subnormal magnitudes. A separate ASan/UBSan executable
covers signed zero, infinities, NaNs, domain-invalid `acosf`, zero divisors,
and exact finite remainders.

## Historical excluded math boundary

The remaining `sinf`, `cosf`, and `tanf` musl implementations require the
double-precision argument-reduction closure. Under the observed G2
`fpv5-sp-d16` build that closure introduces binary64 runtime imports which
have not been reviewed or admitted. The remaining `sqrt` API is binary64 and
likewise depends on a separately justified software runtime or optional
double-precision target capability. None is implemented by guessing from a
prototype.

A subsequent independently audited FPv5-D16 provider now closes those four
symbols without ELF imports and moves the current residual from 31 to 27. See
`g2-lvgl-math-dp-provider-source-admission.md`. The exclusion above remains
the historical boundary of this single-precision tranche and does not itself
authorize production routing.

The 10-symbol FreeRTOS LVGL OSAL remains excluded because the exact
`LV_USE_FREERTOS_TASK_NOTIFY` selection and scheduler/global-state ABI have
not been authenticated. `utf8_codepoint_size` remains excluded because the
private GPU patch does not establish its malformed-UTF-8 policy.

## Reproduction and hardware boundary

From `g2`:

```sh
python3 tools/audit_g2_lvgl_nema_link.py \
  --write-manifest tools/manifests/g2-lvgl-nema-link-admission.json
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_math_provider
python3 -m unittest -v tests.test_audit_g2_lvgl_nema_link
```

No authorized physical target identity, transport, FPU-status capture, GPU
trace, framebuffer capture, or display observation was supplied. Live target
floating-point behavior, Nema rendering, and production collision/routing
therefore remain blocked by unavailable physical and integration evidence.

A subsequent notify-mode-independent four-symbol LVGL mutex provider moves the
current residual to 31; see `g2-lvgl-mutex-provider-source-admission.md`. The
35-symbol count above remains the historical result at this math tranche.
