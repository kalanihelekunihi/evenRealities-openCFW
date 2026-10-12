.section .text.start,"ax",@progbits
.global _start
_start:
    lrw sp, 0x22000000
    jsri main
    lrw r1, 0xffffc000
    st.w r0, (r1,0)
1:  br 1b
