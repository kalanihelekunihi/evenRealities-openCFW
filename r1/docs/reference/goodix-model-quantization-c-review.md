# Native model quantization callbacks in C

`native_model_quantization.c` implements six native ABI entries: rounding at
`0x290fe`, quantization index at `0x6fe20`, parameter derivation at `0x35e34`,
quantization at `0x293fc`, residual addition at `0x36c7c`, and dequantization at
`0x30534`. Three executor-address imports now resolve to real C functions.
No assembly, opcode arrays, fallback execution or writable global state is added.

Parameter derivation preserves inclusion of zero, the initial epsilon width,
bitwise fraction gate, asymmetric endpoint nudges and store order. Quantization
processes batches*rows*columns and updates output range/type even for empty data.
Addition and dequantization process rows*columns, ignoring batch count as native
does. Addition retains direct unclamped steps and wrapped zero-index arithmetic.
Dequantization clips its zero point and preserves forward overlapping writes.

The saturation operation is an architectural C compiler intrinsic. Raw Thumb
bytes decode as SSAT #8, despite REA pseudocode displaying the encoded immediate
#7. The dequantizer has no Ghidra function-manager entry; authenticated Thumb
callback `0x30535`, REA raw-byte readback and Capstone identify its 156-byte body.

Verification passes 40,685 direct comparisons, including 113 independent
numerical cases and twelve positive defect baselines. Another 5,472 comparisons
execute actual C constructors/getter and indirect C callbacks; 864 use the normal
build objects. Tests cover 32 FP configurations, signed zeros, NaNs, infinities,
tiny/reversed ranges, aliases and distinct batch rules. All 278 native instruction
starts /900 body bytes execute. Separate SSAT tests pass 139,268 comparisons,
including every signed16 input, random32 inputs and both incoming sticky-Q values.
Twelve compiled defects are rejected.

All 922 normal units compile and compose without failures or duplicate strong
symbols. All 911 previous nongenerated source/object pairs are unchanged. The
normal provider matches tested sections and decoded symbols after normalizing
source-file metadata. Source plan and health-cache layout are unchanged.
Application imports fall from80 to77; boot imports remain22.

[Machine-readable evidence](goodix-model-quantization-c-review.json) includes
hashes and proof boundaries. Ten callback bindings remain in the actual import
list (correcting the prior narrative count). The inference graph and five parent
SpO2 stages remain open. Public RAM/full FPSCR, saved registers, SP and masks are
checked; private stack and caller-clobbered scratch/APSR are outside the general
contract. Physical hardware, timing, interrupts and full startup remain untested.
