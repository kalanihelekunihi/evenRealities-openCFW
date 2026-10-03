# Independent review 6435

Disposition: **PASS_SCOPED**; `accepted:false`.

Packet hashes and the EE00..EE6C source slice match. GNU Thumb decoding confirms the two disabled guards return original R0 unchanged: the first tests a freshly loaded literal-backed byte, the second tests input R1 after u8 truncation. The enabled path extracts input bits 6..19, multiplies by 1190 with 32-bit wrapping, and shifts right 12 before unsigned integer-to-float conversion.

The VFP sequence is `1 - parameter`, divide, load coefficient and PC-relative float, VMLA, multiply by another PC-relative float, then divide by a third PC-relative float. The instructions are distinct, including VMLA; no fused-operation substitution is assumed. It preserves original R0 bits31..20 separately, performs VCVT.U32.F32, then shifts the result left 6, left 14, and right 14 before ORing the saved upper 12 bits. Consequently the enabled result clears bits 0..5 and 18..19 and retains the original bits20..31; it does not preserve every bit outside the source field.

This is static instruction evidence only. VFP/FPSCR edge behavior and conversion results were not executed or generalized. No calibration-purpose, C, or admission claim; canonical files and gates unchanged.
