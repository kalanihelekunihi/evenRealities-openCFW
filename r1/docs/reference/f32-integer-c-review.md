# Sensor math integer conversions in C

The existing `native_expf_tanhf.c` provider now uses the shared
`native_f32_integer.h` implementation for its signed and unsigned float-to-integer
conversions. This replaces two inline assembly sites. Other arithmetic assembly
in that unit remains. There is no new firmware state or imported dependency.

The integer implementation decodes binary32 without undefined C casts. It
preserves round-toward-zero behavior, signed and unsigned invalid saturation,
NaN-to-zero behavior, flushed-input/denormal status, inexact status and incoming
FPSCR condition/control/sticky bits through compiler FPSCR intrinsics.

## Verification

- 393,216 paired comparisons against actual Cortex-M4 VCVT instructions cover
  6,144 input encodings under 32 FP configurations: all rounding modes, FZ/DN
  combinations, and clear/set sticky flags.
- 264,960 expf/tanhf comparisons against the preceding accepted source provider
  pass with the normal compiler profile. An additional compilation profile
  passes another 264,960 comparisons. Each checks return S0, full FPSCR, public
  RAM outside an 8,192-byte private stack range, saved R4-R11/S16-S31, SP and
  interrupt masks. The source runs with no stock code mapped.
- A further 132,480 comparisons execute stock expf at `0x38f08` against the new
  normal-profile source with the same full checks. Stock application SHA-256:
  `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
- Four independently compiled defects are rejected: lost sticky flags, lost
  flushed-input status, incorrect unsigned-negative status, and NaN saturation.
- The normal source build compiles 916 units without failures or duplicate
  strong symbols. Imports remain 85 application / 22 boot. The production
  provider's sections, relocations and decoded symbols match the tested normal
  object after normalizing only source-file symbol/string metadata.

See [machine-readable evidence](f32-integer-c-review.json) for source, object,
script and result hashes, the exact unchanged-unit count, and comparison limits.
The source plan and health-cache linker layout are unchanged. No hardware flash
or physical sensor test was performed; relocatable composition is not a complete
bootable firmware image.

REA also confirmed the next quality-stage final score clamp at `0x890c8` as
binary32 100.0, and retained the quality/summary dependency dossiers in
`build/goal-r1-quality-c/`. Those stages remain implementation work.
