.syntax unified
.thumb

.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry,%function
.thumb_func
opencfw_closure_entry:
    ldr r0, =opencfw_ccb
    ldr r1, =opencfw_msg
    bl dmConnSmExecute
1:  b 1b
.size opencfw_closure_entry, .-opencfw_closure_entry

.macro RETURN_STUB name
.section .text.\name,"ax",%progbits
.global \name
.type \name,%function
.thumb_func
\name:
    bx lr
.size \name, .-\name
.endm

RETURN_STUB dmConnSmActNone
RETURN_STUB WsfTrace

.section .bss.opencfw_ccb,"aw",%nobits
.align 2
.global opencfw_ccb
opencfw_ccb:
    .space 512
.size opencfw_ccb, .-opencfw_ccb

.section .bss.opencfw_msg,"aw",%nobits
.align 2
.global opencfw_msg
opencfw_msg:
    .space 512
.size opencfw_msg, .-opencfw_msg

.section .note.GNU-stack,"",%progbits
