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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-size-clamps-round319/probe/native-oracle.bin",0,3523364
.section .text.call_probe,"ax"
.global call_probe
.thumb_func
call_probe:
 push {r4-r11,lr}
 sub sp,sp,#4
 mov r12,r0
 mov r0,r1
 mov r1,r2
 mov r2,r3
 ldr r3,[sp,#40]
 ldr r4,=0x20015000
 str sp,[r4,#40]
 movw r4,#0x4444
 movw r5,#0x5555
 movw r6,#0x6666
 movw r7,#0x7777
 movw r8,#0x8888
 movw r9,#0x9999
 movw r10,#0xaaaa
 movw r11,#0xbbbb
 blx r12
 ldr r1,=0x20015000
 str r0,[r1],#4
 stmia r1!,{r4-r11}
 mov r2,sp
 str r2,[r1]
 add sp,sp,#4
 pop {r4-r11,pc}
