# Image-B float power core provenance

The separate image-B candidate's `backup_power_float_core.c` adapts the Sun
fdlibm float `e_powf.c` carried at glibc tag `glibc-2.3` commit
`451c8c22c68df72324fb61b462e24e4778c5fe23`, path
`sysdeps/ieee754/flt-32/e_powf.c`. The exact pinned upstream source is
`upstream-glibc-2.3-e_powf.c` (SHA256
`02e4fab31121173c4af9c9e9bc9cf7df45e5456063975abf5a472f5d91bced58`).
Sun's notice in both source files permits copying and modification provided the
notice is preserved.

Native image-B `binh_b_stage2.bin` SHA256
`d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941`,
base `0x10003000`. Native core `0x100100bc` loads fdlibm polynomial constants
`0x3e6c3255`, `0x3e53f142`, split `cp_h=0x3f763800`,
`cp_l=0x369dc3a0` and the matching exp coefficients. Its valid ISA
continuations include the huge-exponent and underflow paths omitted by the
Ghidra body ranges; `native_power_core_100100bc.disasm` records these.
The candidate preserves native fixed quiet NaN (`0x7fc00000` at `0x10011298`)
and native huge-y near-one lower comparison (`0x3f7ffff7` at `0x100105d4`).

Open equivalence: target FPU rounding/exception flags, exact instruction-level
ordering of fused operations, native sqrt at `0x10010bcc`, and subnormal scale
call at `0x10011194`. The C source exposes both children as typed imports;
it is not a complete-image or physical-runtime proof.

Connected source providers are now included:
- `backup_float_primitives.c`: native quiet NaN `0x10011298` and bitwise
  absolute float `0x100112c4`; checked at exact ISA instructions.
- `backup_sqrtf.c`: bit-by-bit `0x10010bcc` including native final round;
  adapted from the same glibc-2.3 fdlibm source. Pinned source
  `upstream-glibc-2.3-e_sqrtf.c`, SHA256
  `474ea5d9e8c3200506ecb8eda7eb8c4cb3966fb75e41ff888f71d6e49e80cf55`.
- `backup_scalbnf.c`: native `0x10011194` (not an independent Ghidra
  catalogue lead), including signed tiny/huge paths and exponent mutation.
  Pinned source `upstream-glibc-2.3-s_scalbnf.c`, SHA256
  `1481ed4c658a049705af2c22035ba947121f9c502e3fc9a2a48d688e51f12ace`.

Host sanity checks: `verify_sqrtf_host.c` matched 49,759 finite positive
patterns exactly (241 specials excluded); `verify_scalbnf_host.c` matched
179,307 finite input/exponent pairs exactly (77 specials excluded);
`verify_power_core_host.c` matched 106 representative finite pairs exactly
and four domain NaNs. These checks establish ordinary arithmetic behavior,
not C-SKY FPU flags or physical runtime equivalence.

Connected logarithm path:
- Native `0x100100ac` is a hard-float call-through to `0x10010768`.
- `backup_logf.c` reconstructs native `0x10010768` from pinned Sun fdlibm
  `e_logf.c`, glibc-2.3 commit above. The native pool at
  `0x10010994..0x100109bc` matches all seven polynomial coefficients plus
  `ln2_hi=0x3f317180`, `ln2_lo=0x3717f7d1`. Pinned file
  `upstream-glibc-2.3-e_logf.c`, SHA256
  `71704d3c512136c0c40e2ebc72d5b10caf4e5d03b738b5a218be506f43340ef4`.
- Host sanity `verify_logf_host.c`: 29,683 exact finite positive results,
  190 within 1e-6 relative/absolute scale, 127 excluded specials, zero
  mismatches. This is bounded algorithm evidence, not original C-SKY
  instruction/exception equivalence.

C-SKY target result: `build-fdlibm-round/receipt.json` compiles 129/129 units
and `ld -r` succeeds. Linked object SHA256
`f2749202bcbf2aa938c479d2ab3e588eaa890db7c3ef1775a0ce20da18eb812f`.
The only unresolved names are `__fe_getround`, `__fe_raise_inexact`,
`gx8002_image_b_native_word_at_zero_1000ada6`, and
`gx8002_image_b_uart_dma_ambient_direction_100040e8`; neither power,
logarithm, square root nor scale adds a remaining import. Compiled object
literal bytes match native for five chosen power constants, four log
constants and two scale overflow/underflow constants. This is constant
and target build evidence, not full instruction trace equivalence.
