/* Oracle-only nonimplementation: exposes any remaining FP-exception call. */
.section .text.oracle_fp,"ax",@progbits
.global __fe_raise_inexact
__fe_raise_inexact:
    lrw r1, 0xffffc000
    lrw r0, 91
    st.w r0, (r1,0)
1:  br 1b
