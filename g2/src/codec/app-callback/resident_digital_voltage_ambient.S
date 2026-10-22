/* SPDX-License-Identifier: MIT
 * Exact instruction-level 0x10024730 digital-voltage body. The native code
 * reads the first byte of its newly allocated stack slot before writing it;
 * this ambient value is preserved, not invented as zero in C.
 */
    .text
    .align 2
    .global gx8002_resident_digital_voltage_24730
    .type gx8002_resident_digital_voltage_24730, %function
/* Stock 0x10024730 (gx8002_digital_voltage) */
gx8002_resident_digital_voltage_24730:
    push r15
    subi r14, r14, 4
    movi r3, 0
    subi r3, r3, 1
    cmpne r0, r3
    bf 1f
    ld.b r3, (r14, 0)
    ins r3, r0, 3, 0
    movi r2, 1
    ins r3, r2, 4, 4
    mov r1, r14
    movi r0, 8
    st.b r3, (r14, 0)
    bsr gx8002_resident_platform_config_25d74
    movi r0, 0
1:  addi r14, r14, 4
    pop r15
    .size gx8002_resident_digital_voltage_24730, .-gx8002_resident_digital_voltage_24730
