.syntax unified
.thumb
.section .vectors,"a",%progbits
.word 0x2003f000
.word Reset_Handler+1
.rept 14
.word 0
.endr
.section .text.startup,"ax",%progbits
.global Reset_Handler
.type Reset_Handler,%function
.thumb_func
Reset_Handler:
 bl main
 movs r0,#0x18
 ldr r1,=0x20026
 bkpt #0xab
 b .
.section .stock,"ax",%progbits
.incbin "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
