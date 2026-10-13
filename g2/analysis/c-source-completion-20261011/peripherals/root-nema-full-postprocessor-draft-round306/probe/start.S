.section .note.GNU-stack,"",%progbits
.syntax unified
.thumb
.section .vectors,"a"
.word 0x2007ff00
.word reset_entry
.rept 14
.word fault_handler
.endr
.section .reset,"ax"
.global reset_entry
.thumb_func
reset_entry: ldr r0,=0xe000ed88
ldr r1,[r0]
orr r1,r1,#0xf00000
str r1,[r0]
dsb
isb
bl main
b .
.section .native_main,"ax"
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-nema-full-postprocessor-draft-round306/probe/native-oracle-bound.bin",0,3523364
.section .text.abi_probe,"ax"
.global abi_probe
.thumb_func
abi_probe:
 push {r4-r11,lr}
 vpush {d8-d15}
 sub sp,sp,#4
 mov r12,r0
 mov r0,r1
 ldr r2,=0x20016000
 str sp,[r2,#100]
 ldr r2,=abi_fp_seeds
 vldmia r2,{d8-d15}
 movw r4,#0x4444
 movw r5,#0x5555
 movw r6,#0x6666
 movw r7,#0x7777
 movw r8,#0x8888
 movw r9,#0x9999
 movw r10,#0xaaaa
 movw r11,#0xbbbb
 blx r12
 ldr r0,=0x20016000
 stmia r0!,{r4-r11}
 mov r1,sp
 str r1,[r0],#4
 vstmia r0,{d8-d15}
 add sp,sp,#4
 vpop {d8-d15}
 pop {r4-r11,pc}
.section .rodata.abi_seeds,"a"
.align 2
abi_fp_seeds:
.word 0x3f800001,0xbf800002,0x00000001,0x80000002
.word 0x7fc12345,0x7f812345,0x7f800000,0xff800000
.word 0x3e800003,0xbe800004,0x00000000,0x80000000
.word 0x00800000,0x007fffff,0x7f7fffff,0xff7fffff
