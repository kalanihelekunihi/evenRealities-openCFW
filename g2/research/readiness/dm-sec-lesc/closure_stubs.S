.syntax unified
.thumb
.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry,%function
.thumb_func
opencfw_closure_entry:
    bl DmSecLescInit
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
ZERO_STUB Calc128Cpy
ZERO_STUB dmEmptyHandler
ZERO_STUB dmEmptyReset
ZERO_STUB memcpy
ZERO_STUB memset
ZERO_STUB SecCmac
ZERO_STUB SecEccGenKey
ZERO_STUB SmpDmMsgSend
ZERO_STUB smpLogByteArray
ZERO_STUB SmpScCat
ZERO_STUB SmpScGetCancelMsgWithReattempt
ZERO_STUB SmpScSetOobCfg
ZERO_STUB WsfBufAlloc
ZERO_STUB WsfBufFree
ZERO_STUB WsfMsgAlloc
ZERO_STUB WsfTrace
.section .bss.dmCb,"aw",%nobits
.align 2
.global dmCb
dmCb: .space 4096
.size dmCb,.-dmCb
.section .bss.dmFcnIfTbl,"aw",%nobits
.align 2
.global dmFcnIfTbl
dmFcnIfTbl: .space 1024
.size dmFcnIfTbl,.-dmFcnIfTbl
.section .note.GNU-stack,"",%progbits
