.syntax unified
.thumb
.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry,%function
.thumb_func
opencfw_closure_entry:
    movs r0,#0
    movs r1,#0
    movs r2,#0
    bl DmSmpEncryptReq
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
ZERO_STUB dmConnCcbById
ZERO_STUB HciLeStartEncryptionCmd
ZERO_STUB memcpy
ZERO_STUB SmpDmMsgSend
ZERO_STUB WsfMsgAlloc
ZERO_STUB WsfMsgSend
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
.section .note.GNU-stack,"",%progbits
