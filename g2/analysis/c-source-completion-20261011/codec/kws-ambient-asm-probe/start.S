.section .text.start,"ax",@progbits
.global _start
_start:
    lrw sp, 0x22000000
    mov r4, sp
    subi r4, r4, 60
    lrw r3, 0x11223344
    st.w r3, (r4, 0)
    lrw r3, 0x55667788
    st.w r3, (r4, 12)
    lrw r3, 0x99aabbcc
    st.w r3, (r4, 16)
    jbsr gx8002_xip_kws_flash_load_10206cb0
    lrw r4, 0x2002e85c
    lrw r1, 0xffffc040
    movi r2, 0
1:
    ld.w r3, (r4, 0)
    st.w r3, (r1, 0)
    addi r4, 4
    addi r2, 1
    cmpnei r2, 8
    bt 1b
    lrw r1, 0xffffc000
    movi r0, 0
    st.w r0, (r1, 0)
2:  br 2b
