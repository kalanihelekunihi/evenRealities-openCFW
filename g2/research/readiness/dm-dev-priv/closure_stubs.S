.syntax unified
.thumb

.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry,%function
.thumb_func
opencfw_closure_entry:
    bl DmDevPrivInit
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
ZERO_STUB BdaIsZeros
ZERO_STUB DmAdvSetAddrType
ZERO_STUB DmConnSetAddrType
ZERO_STUB DmPrivClearResList
ZERO_STUB DmPrivSetResolvablePrivateAddrTimeout
ZERO_STUB DmScanSetAddrType
ZERO_STUB DmSecGetLocalIrk
ZERO_STUB HciLeSetRandAddrCmd
ZERO_STUB HciLlPrivacySupported
ZERO_STUB memcpy
ZERO_STUB memset
ZERO_STUB SecAes
ZERO_STUB SecRand
ZERO_STUB WsfAssert
ZERO_STUB WsfMsgAlloc
ZERO_STUB WsfMsgSend
ZERO_STUB WsfTaskLock
ZERO_STUB WsfTaskUnlock
ZERO_STUB WsfTimerStartSec
ZERO_STUB WsfTimerStop

.section .bss.dmCb,"aw",%nobits
.align 2
.global dmCb
dmCb:
    .space 4096
.size dmCb, .-dmCb

.section .bss.dmDevCb,"aw",%nobits
.align 2
.global dmDevCb
dmDevCb:
    .space 256
.size dmDevCb, .-dmDevCb

.section .bss.dmFcnIfTbl,"aw",%nobits
.align 2
.global dmFcnIfTbl
dmFcnIfTbl:
    .space 1024
.size dmFcnIfTbl, .-dmFcnIfTbl

.section .note.GNU-stack,"",%progbits
