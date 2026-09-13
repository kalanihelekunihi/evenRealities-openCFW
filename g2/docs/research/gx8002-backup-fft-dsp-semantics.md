# Backup FFT instruction evidence

The radix-4-by-2 routines occupy package offsets 0x47bf4..0x47c98
(forward) and 0x47c98..0x47d3c (inverse). Both preserve r4-r6,
process length/2 packed complex samples, call the corresponding radix-4
helper twice with coefficient stride 2, then double each 16-bit sample.
This description is decoded control-flow evidence; arithmetic replacement
has not yet been qualified.

Vendor emulator source is pinned at XUANTIE-RV/qemu commit
3287d345c7f5d60d5c8774d90752f5f710744f85. File blob and SHA-256 identities
are recorded in gx8002-csky-dsp-upstream-evidence.json. Downloaded copies
are in build/upstream-xuantie-qemu-csky. They are instruction-reference
material, not firmware dependencies or source replacement bytes.

Relevant implementations:

- `target/csky/op_dspv2.c`, `DSPV2_HELPER(paddh_s16)`: independently
  sign-extend the two 16-bit lanes, add each pair at 32-bit width, then
  arithmetic-shift each sum by one and pack the low 16 bits.
- `target/csky/translate_v2.c`, `dspv2_insn_pasri_s16`: arithmetic right
  shift of each signed 16-bit lane independently.
- `dspv2_insn_pmul_s16`: low*low product in destination, high*high in
  destination+1 (modulo 32 registers).
- `dspv2_insn_pmulx_s16`: low*high product in destination, high*low in
  destination+1. Its inline comment incorrectly describes the non-crossed
  variant; the actual TCG operand wiring is the evidence used here.
- `case 0xe /* bloop */`: subtract one from the loop register, then branch
  if nonzero. This supports the existing positive-count do/while recovery
  of the bit-reversal leaf. Zero-count wrap and branch encoding still need
  explicit qualification; emulator behavior alone is not hardware testing.

In the forward butterfly, the packed difference is multiplied by the
coefficient pair: real uses the sum of same-lane products; imaginary uses
high*low minus low*high. The inverse uses the difference of same-lane
products and the sum of crossed products. Results are arithmetic-shifted
by 16 before halfword stores. Preserve 32-bit wrapping when translating
product combinations, and preserve per-lane half shifts before subtraction.

Source links:
https://github.com/XUANTIE-RV/qemu/blob/3287d345c7f5d60d5c8774d90752f5f710744f85/target/csky/op_dspv2.c
https://github.com/XUANTIE-RV/qemu/blob/3287d345c7f5d60d5c8774d90752f5f710744f85/target/csky/translate_v2.c
