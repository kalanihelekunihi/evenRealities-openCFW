.syntax unified
.thumb
.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry,%function
.thumb_func
opencfw_closure_entry:
    bl DmSecInit
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
ZERO_STUB DmConnSetIdle
ZERO_STUB HciLeLtkReqNegReplCmd
ZERO_STUB HciLeLtkReqReplCmd
ZERO_STUB HciLeStartEncryptionCmd
ZERO_STUB memcmp
ZERO_STUB memcpy
ZERO_STUB SmpDbInit
ZERO_STUB SmpDmEncryptInd
ZERO_STUB SmpDmGetStk
ZERO_STUB SmpDmLescEnabled
ZERO_STUB SmpDmMsgSend
ZERO_STUB WsfAssert
ZERO_STUB WsfMsgAlloc
ZERO_STUB WsfMsgSend
ZERO_STUB WsfTaskLock
ZERO_STUB WsfTaskUnlock
.section .bss.calc128Zeros,"aw",%nobits
.align 2
.global calc128Zeros
calc128Zeros: .space 16
.size calc128Zeros,.-calc128Zeros
.section .bss.dmCb,"aw",%nobits
.align 2
.global dmCb
dmCb: .space 4096
.size dmCb,.-dmCb
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
