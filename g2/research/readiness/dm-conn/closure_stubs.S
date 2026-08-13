.syntax unified
.thumb

.section .text.opencfw_closure_entry,"ax",%progbits
.global opencfw_closure_entry
.type opencfw_closure_entry, %function
.thumb_func
opencfw_closure_entry:
  bl DmConnInit
1:
  b 1b
.size opencfw_closure_entry, .-opencfw_closure_entry

.macro OPENCFW_STUB name
  .global \name
  .type \name, %function
  .thumb_func
\name:
  movs r0, #0
  bx lr
  .size \name, .-\name
.endm

OPENCFW_STUB BdaCmp
OPENCFW_STUB BdaCpy
OPENCFW_STUB DmHostAddrType
OPENCFW_STUB DmInitPhyToIdx
OPENCFW_STUB HciDisconnectCmd
OPENCFW_STUB HciGetBdAddr
OPENCFW_STUB HciLeReadRemoteFeatCmd
OPENCFW_STUB HciLeRemoteConnParamReqNegReply
OPENCFW_STUB HciLeRemoteConnParamReqReply
OPENCFW_STUB HciLeRequestPeerScaCmd
OPENCFW_STUB HciLeSetDataLen
OPENCFW_STUB HciReadRemoteVerInfoCmd
OPENCFW_STUB HciReadRssiCmd
OPENCFW_STUB HciWriteAuthPayloadTimeout
OPENCFW_STUB WsfAssert
OPENCFW_STUB WsfMsgAlloc
OPENCFW_STUB WsfMsgSend
OPENCFW_STUB WsfTaskLock
OPENCFW_STUB WsfTaskUnlock
OPENCFW_STUB WsfTrace
OPENCFW_STUB dmConnSmExecute
OPENCFW_STUB dmDevPassEvtToConnCte
OPENCFW_STUB dmDevPassEvtToDevPriv
OPENCFW_STUB dmEmptyHandler
OPENCFW_STUB dmEmptyReset
OPENCFW_STUB memcpy
OPENCFW_STUB memset

.section .bss.opencfw_closure_objects,"aw",%nobits
.align 2
.global dmCb
.type dmCb, %object
dmCb:
  .space 4096
.size dmCb, .-dmCb

.align 2
.global dmConnActSet
.type dmConnActSet, %object
dmConnActSet:
  .space 256
.size dmConnActSet, .-dmConnActSet

.align 2
.global dmFcnIfTbl
.type dmFcnIfTbl, %object
dmFcnIfTbl:
  .space 256
.size dmFcnIfTbl, .-dmFcnIfTbl
