/* Source ABI adapter for stock41c4b4; no executable blob/opcode payload. */
.syntax unified
.thumb
.section .text.opencfw_boot_startup_initialize_abi,"ax",%progbits
.global opencfw_boot_startup_initialize_abi
.type opencfw_boot_startup_initialize_abi,%function
.thumb_func
opencfw_boot_startup_initialize_abi:
 push {r1,r2,r3,r4,r5,lr}
 sub sp,sp,#24
 str r5,[sp,#0]
 str r7,[sp,#4]
 ldr r0,[sp,#24]
 str r0,[sp,#8]
 ldr r0,[sp,#28]
 str r0,[sp,#12]
 ldr r0,[sp,#32]
 str r0,[sp,#16]
 mov r0,sp
 bl reconstructed_initialize_clock_coupled_abi_core
 ldr r1,[sp,#8]
 str r1,[sp,#24]
 ldr r1,[sp,#12]
 str r1,[sp,#28]
 ldr r1,[sp,#16]
 str r1,[sp,#32]
 add sp,sp,#24
 pop {r1,r2,r3,r4,r5,pc}
.size opencfw_boot_startup_initialize_abi,.-opencfw_boot_startup_initialize_abi
.section .note.GNU-stack,"",%progbits
