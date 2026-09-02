# G2 bootloader floating multiplier helper source closure

This note records the software-only clean-room recovery of the bootloader
function at `[0x00426EAC, 0x00426F6A)`. It does not claim device execution or
hardware qualification.

## Authenticated stock evidence

- Stock span: 190 bytes, SHA-256
  `d289cc7f7ccd0c61ba49a4bf7c176573ceebe7d8725720ac00459716c6852cad`.
- Sole direct caller: `0x00426FE6`; no interior direct callers or stored
  interior Thumb entry pointers were found.
- The caller supplies output pointers in `r0` through `r2` and floating inputs
  in `s0` and `s1`. The retained `ceilf`, `fmodf`, `roundf`, and `floorf`
  veneers likewise consume and return values through VFP registers. The
  production C entry and every retained-provider declaration therefore use
  explicit `pcs("aapcs-vfp")` on Arm/Thumb builds.
- Provider edges are `ceilf` at stock offset `0x2A`, `fmodf` at `0x62`,
  `roundf` at `0x6E`, and `floorf` at `0x7A` and `0x9E`.
- Apollo-main contains a 190-byte analogue at
  `[0x005394E0, 0x0053959E)`, SHA-256
  `5a1e7e7a8314532a36fd1b59a8f75d13d041bfbc1bb4fa75fa8c5949fac37562`.
  It agrees in 173 of 190 bytes; the differences are confined to eight runs,
  including address-coupled provider calls.

## Recovered behavior

The implementation computes `ratio = second / first`, selects
`ceilf(10 / ratio)` as a bounded scale, and rejects scale values below
`2^-23` or at/above `63.0000038`. It then encodes the scaled product as:

- an 8-bit scale;
- a 16-bit integer part, accepted only in `[10, 96.0000076)`; and
- a rounded 24-bit fractional value represented in a 32-bit output word.

All rejection paths return zero without publishing partial outputs. A valid
encoding writes all three outputs and returns one.

## Production realization

`components/bootloader/core_overlay/runtime_float_multiplier_426eac.c` is
MIT-licensed reviewable C. With the reviewed Apple clang 21.0.0 and Homebrew
clang 22.1.8 profiles it compiles identically to a 192-byte Thumb function.
The machine outliner is explicitly disabled for this isolated leaf so the
strict closure contains one selected text section and no hidden local helper.

- Cave: `[0x00415DE4, 0x00415EA4)`.
- Relocated SHA-256:
  `31c6cef0307e4b967a1528c06e5b9d8dc8d37be1dbf651f2cf76a6a9eed58004`.
- Unrelocated SHA-256:
  `3bed1abbdaa0269020d633558de15214c147f98916119dee54d1f1ea054d240a`.
- Relocation offsets: `0x18`, `0x52`, `0x5E`, `0x6A`, and `0x8C`.

The authenticated stock entry is replaced by a `B.W` redirect and generated
NOP fill. Host semantic tests, both reviewed compiler profiles, strict
relocation checks, caller/provider ABI windows, package ownership accounting,
and the complete software build route are locally verifiable.

Hardware validation is blocked by unavailable physical evidence.
