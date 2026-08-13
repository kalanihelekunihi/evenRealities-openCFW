.syntax unified
.thumb
.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry,%function
.thumb_func
opencfw_closure_entry:
    bl DmPrivInit
1:  b 1b
.size opencfw_closure_entry, .-opencfw_closure_entry
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
ZERO_STUB BdaCpy
ZERO_STUB Calc128Cpy
ZERO_STUB dmDevPassEvtToDevPriv
ZERO_STUB dmEmptyHandler
ZERO_STUB dmEmptyReset
ZERO_STUB HciLeAddDeviceToResolvingListCmd
ZERO_STUB HciLeClearResolvingList
ZERO_STUB HciLeReadLocalResolvableAddr
ZERO_STUB HciLeReadPeerResolvableAddr
ZERO_STUB HciLeRemoveDeviceFromResolvingList
ZERO_STUB HciLeSetAddrResolutionEnable
ZERO_STUB HciLeSetPrivacyModeCmd
ZERO_STUB HciLeSetResolvablePrivateAddrTimeout
ZERO_STUB memcmp
ZERO_STUB memcpy
ZERO_STUB memset
ZERO_STUB SecAes
ZERO_STUB SecRand
ZERO_STUB WsfMsgAlloc
ZERO_STUB WsfMsgSend
ZERO_STUB WsfTaskLock
ZERO_STUB WsfTaskUnlock
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
