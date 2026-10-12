/* Test harness witness only. These remain genuine firmware imports.
 * Any reach of either unresolved FP-environment contract fails the finite
 * fixture through QEMU's exit MMIO; this file is not a candidate provider.
 */
.section .text.oracle_fp,"ax",@progbits
.global __fe_getround
.global __fe_raise_inexact
__fe_getround:
    lrw r1, 0xffffc000
    lrw r0, 90
    st.w r0, (r1,0)
1:  br 1b
__fe_raise_inexact:
    lrw r1, 0xffffc000
    lrw r0, 91
    st.w r0, (r1,0)
2:  br 2b
