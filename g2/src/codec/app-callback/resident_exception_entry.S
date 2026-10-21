/* SPDX-License-Identifier: MIT
 * Native image-A SRAM exception entry. Instruction-level
 * reconstruction of 0x100235f0 and 0x100235fc; no stock bytes
 * or opaque handler stub are embedded. Callback slots remain runtime input.
 */
    .text
    .align 2
    .global gx8002_resident_trap_c_235f0
    .type gx8002_resident_trap_c_235f0, %function
gx8002_resident_trap_c_235f0:
    mfcr r3, cr<0, 0>
    lsri r3, r3, 16
    sextb r3, r3
1:  br 1b
    .size gx8002_resident_trap_c_235f0, .-gx8002_resident_trap_c_235f0

    .align 2
    .global gx8002_resident_trap_235fc
    .type gx8002_resident_trap_235fc, %function
gx8002_resident_trap_235fc:
    psrset ee
    subi r14, r14, 4
    st.w r13, (r14, 0)
    addi r14, r14, 4
    lrw r13, 0x20027310
    st.w r14, (r13, 0)
    lrw r14, 0x20027310
    subi r14, r14, 72
    stm r0-r12, (r14)
    lrw r0, 0x20027310
    ld.w r0, (r0, 0)
    st.w r0, (r14, 0x38)
    subi r0, r0, 4
    ld.w r13, (r0, 0)
    st.w r13, (r14, 0x34)
    st.w r15, (r14, 0x3c)
    mfcr r0, cr<2, 0>
    st.w r0, (r14, 0x40)
    mfcr r0, cr<4, 0>
    st.w r0, (r14, 0x44)
    mov r0, r14
    bsr gx8002_resident_trap_c_235f0
2:  br 2b
    .size gx8002_resident_trap_235fc, .-gx8002_resident_trap_235fc

