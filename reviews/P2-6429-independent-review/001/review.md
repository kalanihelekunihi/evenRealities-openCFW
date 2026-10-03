# Independent review 6429

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet and EC6E..ECF2 source hashes match. GNU Thumb decoding confirms the frameless mode-1 continuation. A null descriptor returns 6. It loads descriptor float +8 and compares against the PC-relative float literal at EDF8; BNE returns 7, including the unordered comparison case. On equality it loads the input float and three source coefficients, then reads the current offset through a literal-backed pointer and compares it with zero. BNE skips lazy initialization, again including unordered NaN.

The zero-offset branch stores the PC-relative initial offset, then uses separate VFP single-precision operations and fresh offset reloads: add coefficients, reload offset, multiply, store; reload, add the next coefficient, store. The common branch then multiplies the input by the PC-relative coefficient at EDFC, freshly reloads and adds the offset, adds the literal at EE6C, stores the resulting float to descriptor+4, and branches to the common zero return. The decoded operations are separate VADD/VMUL/VSTR/VLDR instructions; no fused operation is present in this path.

This is instruction-level evidence only. FPSCR side effects and runtime numerical behavior are not independently executed or generalized; no API or canonical/admission claim is made. No canonical files or gates changed.
