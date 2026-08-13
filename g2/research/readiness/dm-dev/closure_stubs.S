.syntax unified
.thumb

.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry,%function
.thumb_func
opencfw_closure_entry:
    bl DmDevReset
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

ZERO_STUB BdaCpy
ZERO_STUB dmEmptyReset
ZERO_STUB HciLeAddDevWhiteListCmd
ZERO_STUB HciLeClearWhiteListCmd
ZERO_STUB HciLeRemoveDevWhiteListCmd
ZERO_STUB HciLeSetRandAddrCmd
ZERO_STUB HciResetSequence
ZERO_STUB HciVsInit
ZERO_STUB WsfAssert
ZERO_STUB WsfMsgAlloc
ZERO_STUB WsfMsgSend
ZERO_STUB WsfTrace

.section .bss.dmCb,"aw",%nobits
.align 2
.global dmCb
dmCb:
    .space 4096
.size dmCb, .-dmCb

.section .bss.dmFcnIfTbl,"aw",%nobits
.align 2
.global dmFcnIfTbl
dmFcnIfTbl:
    .space 1024
.size dmFcnIfTbl, .-dmFcnIfTbl

.section .note.GNU-stack,"",%progbits
