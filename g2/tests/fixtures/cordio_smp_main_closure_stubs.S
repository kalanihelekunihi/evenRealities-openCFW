.syntax unified
.thumb

.macro OPENCFW_STUB name
  .global \name
  .type \name, %function
  .thumb_func
\name:
  movs r0, #0
  bx lr
  .size \name, .-\name
.endm

OPENCFW_STUB BdaIsZeros
OPENCFW_STUB Calc128Cpy64
OPENCFW_STUB DmConnIdByHandle
OPENCFW_STUB DmConnLocalAddr
OPENCFW_STUB DmConnLocalAddrType
OPENCFW_STUB DmConnLocalRpa
OPENCFW_STUB DmConnPeerAddr
OPENCFW_STUB DmConnPeerAddrType
OPENCFW_STUB DmConnPeerRpa
OPENCFW_STUB DmConnRegister
OPENCFW_STUB DmConnRole
OPENCFW_STUB DmSmpCbackExec
OPENCFW_STUB L2cDataReq
OPENCFW_STUB L2cRegister
OPENCFW_STUB SecAes
OPENCFW_STUB SecRand
OPENCFW_STUB SmpDbGetFailureCount
OPENCFW_STUB SmpDbGetPairingDisabledTime
OPENCFW_STUB SmpDbInit
OPENCFW_STUB SmpDbService
OPENCFW_STUB SmpDbSetFailureCount
OPENCFW_STUB WsfBufFree
OPENCFW_STUB WsfMsgDataAlloc
OPENCFW_STUB WsfMsgDeq
OPENCFW_STUB WsfMsgFree
OPENCFW_STUB WsfMsgSend
OPENCFW_STUB WsfTimerStartMs
OPENCFW_STUB WsfTrace
OPENCFW_STUB memcpy
OPENCFW_STUB memset
OPENCFW_STUB smpSmExecute

.bss
.align 2
.global secCb
.type secCb, %object
secCb:
  .space 8
.size secCb, .-secCb
