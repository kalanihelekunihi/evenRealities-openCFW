.syntax unified
.thumb
.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry,%function
.thumb_func
opencfw_closure_entry:
    movs r0,#0
    movs r1,#1
    movs r2,#0
    movs r3,#0
    bl DmConnOpen
1:  b 1b
.size opencfw_closure_entry,.-opencfw_closure_entry
.macro ZERO_STUB name
.section .text.\name,"ax",%progbits
.global \name
.type \name,%function
.thumb_func
\name:
    movs r0,#0
    bx lr
.size \name,.-\name
.endm
ZERO_STUB dmConnCcbByHandle
ZERO_STUB dmConnOpenAccept
ZERO_STUB dmConnUpdExecute
ZERO_STUB dmDevPassEvtToDevPriv
ZERO_STUB HciLeConnUpdateCmd
ZERO_STUB HciLeCreateConnCancelCmd
ZERO_STUB L2cDmConnUpdateRsp
ZERO_STUB WsfTaskLock
ZERO_STUB WsfTaskUnlock
.section .bss.dmCb,"aw",%nobits
.align 2
.global dmCb
dmCb: .space 4096
.size dmCb,.-dmCb
.section .note.GNU-stack,"",%progbits
