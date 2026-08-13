.syntax unified
.thumb
.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry,%function
.thumb_func
opencfw_closure_entry:
    movs r0, #7
    bl DmHandlerInit
1:  b 1b
.size opencfw_closure_entry, .-opencfw_closure_entry

.macro ZERO_STUB name
.section .text.\name,"ax",%progbits
.global \name
.type \name,%function
.thumb_func
\name:
    movs r0, #0
    bx lr
.size \name, .-\name
.endm
ZERO_STUB HciEvtRegister
ZERO_STUB HciGetMaxRxAclLen
ZERO_STUB WsfAssert

.section .bss.dmDevFcnIf,"aw",%nobits
.align 2
.global dmDevFcnIf
dmDevFcnIf:
    .space 64
.size dmDevFcnIf, .-dmDevFcnIf
.section .note.GNU-stack,"",%progbits
