# Recovered inverse-real-split arithmetic contract

Bounded source/address family: authentic `csky_split_rifft_q15`, exact-reproduced86-byte section at conditional normal-copy IRAM1000F068 in locked codec BINH Bstage2. Placement/startup/CPU alias visibility remains conditional. This packet executes that source-produced section under smartl in separately mapped RAM, not at assumed target coordinates.

## Layout, iteration and operations

API takes forward-source pointer, complex lengthN, coefficient-A pointer, output pointer and modifier. Target pointer/argument width32bits; assembly fifth modifier argument is read from stack after saving l0. This tested binding uses N256/real512/modifier1. Source forward pair starts at halfword0, reverse pair starts at halfword2N and moves backwards by2; A advances by2*modifier halfwords. Each iteration emits one packed real/imaginary pair. Thus256 iterations write512 halfwords. Source/table data are read only; endpoint input capacity includes src[512] and src[513]. All tested buffers/tables are4-byte aligned.

Let A=(Alo,Ahi), with signed16 lane interpretations. Form temporary packed B'=lane_subtract16(0x00008000,A). Then B=(saturating_abs16(B'lo),B'hi): high lane retains its pre-abs bits. This distinction matters; both lanes are not absolute-valued in final B.

Per iteration, with signed16 forward pair F and reverse pair R:

```text
real_seed = Rlo*Blo - Rhi*Bhi
real_acc  = SAT32(real_seed + Flo*Alo + Fhi*Ahi)
cross     = SAT32(Rlo*Bhi + Rhi*Blo)           // MULCAX standalone
neg_cross = PNEG16(cross_bits)                // TWO signed16 lanes, not NEG32
imag_acc  = SAT32(sign32(neg_cross) + Alo*Fhi - Ahi*Flo)
output_real_bits = high16(real_acc_bits)
output_imag_bits = high16(imag_acc_bits)
```

PNEG16 sign-decodes each16-bit lane, negates with saturation(-32768 ->32767), then packs the lanes. Use explicit wide intermediate arithmetic for the documented MAC equations; QEMU's general extreme MAC implementation is not an oracle for narrowing/wrapping the dual-product intermediate. High16 extraction is an arithmetic right shift/floor for signed values when interpreted as a signed halfword, not round-to-nearest or truncation toward zero.

The authentic C alternative uses scalar32-bit `-cross` in this position. The reviewed separate diagnostic changes only that expression to explicit fixed-width PNEG16 semantics; original source remains untouched. Current source/ISA/model agreement supports this distinction, not physical GX8002 validation or a universal replacement algorithm.

## Exact endpoint discriminator

For source DC/Nyquist pairs both(a,0), all remaining pairszero, first A=(16384,-16384) and derived B=(16384,16384):

```text
p = a * 16384
original_C_imag_acc = -p + p = 0
assembly/model_imag_acc = sign32(PNEG16(bits32(p))) + p
```

As an analytical fixed-domain consequence for a signedQ15 amplitude:

| a residue mod4 | packed accumulator | emitted imaginary halfword |
|---|---:|---:|
|0|0|0|
|1 or3|0x00010000|1|
|2|0x0000ffff|0|

The first real output is floor(a/2) in all three implementations. Twelve selected positive/negative/extreme amplitudes execute and confirm these predictions. The residue2 internal difference is invisible after high16 extraction; equality of final halfwords alone cannot establish identical intermediate arithmetic.

## Evidence tiers and unresolved boundaries

Static exactness: licensed assembly source reproduces the nine selected sections/1606bytes. Source availability/compile-link: authentic alternative's dependency closure links; numerical equality is a separate claim. Original corpus:256 passes, first failure,32 unrun; immutable. Separate negation diagnostic:33 targeted FFT passes, not a56-case diagnostic corpus. New discriminator:12 prediction passes with independent guards/tails, five expected original-C/assembly endpoint differences. Do not add repeated fixtures/probes as unique function or opcode coverage.

E804 retained manual supports the packed-negation equations. The six all-min-pair MAC probes instead demonstrate documented-operation/QEMU-model discrepancies; selected three table-bound real-split assembly MAC sites exclude that specific corner, not every possible backend error. Physical CK804/GX8002 revision/ISA execution, live audio contents, other lengths/tables/callers, startup choice and CPU aliasing remain unverified. First-party DSP/GSC callers and whole-image P2/source/byte-equal rebuilding remain separate work; no new canonical admission or production code follows from these tests.
