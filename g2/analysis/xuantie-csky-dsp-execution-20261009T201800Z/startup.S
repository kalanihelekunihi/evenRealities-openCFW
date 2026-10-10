.section .text.start,"ax",@progbits
.global _start
_start:
 lrw sp, 0x20010000
 jsri main
 lrw r1, 0x10002000
 st.w r0, (r1,0)
1: br 1b
