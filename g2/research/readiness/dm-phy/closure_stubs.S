.syntax unified
.thumb
.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry,%function
.thumb_func
opencfw_closure_entry:
    bl DmPhyInit
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
ZERO_STUB dmConnCcbById
ZERO_STUB dmEmptyHandler
ZERO_STUB dmEmptyReset
ZERO_STUB HciLeReadPhyCmd
ZERO_STUB HciLeSetDefaultPhyCmd
ZERO_STUB HciLeSetPhyCmd
ZERO_STUB HciSetLeSupFeat
ZERO_STUB WsfTaskLock
ZERO_STUB WsfTaskUnlock
.section .bss.dmConnCb,"aw",%nobits
.align 2
.global dmConnCb
dmConnCb: .space 4096
.size dmConnCb,.-dmConnCb
.section .bss.dmFcnIfTbl,"aw",%nobits
.align 2
.global dmFcnIfTbl
dmFcnIfTbl: .space 1024
.size dmFcnIfTbl,.-dmFcnIfTbl
.section .note.GNU-stack,"",%progbits
