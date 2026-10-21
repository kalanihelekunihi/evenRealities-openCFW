/* Native WsfMsgDataAlloc 0x4bf990 and attL2cDataReq 0x4b50ba. */
#include <stdint.h>
extern uint8_t audio_ble_att_common_state[]; /* native attCb 0x200610ac */
extern uint8_t *WsfMsgAlloc(uint16_t length);
extern void L2cDataReq(uint16_t cid,uint16_t handle,uint16_t length,uint8_t *buffer);
extern void WsfMsgFree(void *buffer);

uint8_t *WsfMsgDataAlloc(uint16_t length,uint8_t offset)
{
    return WsfMsgAlloc((uint16_t)(length+offset));
}

void attL2cDataReq(uint8_t *ccb,uint8_t slot,uint16_t length,uint8_t *packet)
{
    if (slot==0u) {
        uint16_t handle=(uint16_t)ccb[0x0cu]|((uint16_t)ccb[0x0du]<<8u);
        L2cDataReq(4u,handle,length,packet);
    } else {
        uint32_t raw;
        __builtin_memcpy(&raw,audio_ble_att_common_state+0x54u,4u);
        if (raw==0u) WsfMsgFree(packet);
        else ((void (*)(uint8_t *,uint8_t,uint16_t,uint8_t *))(uintptr_t)raw)
             (ccb,slot,length,packet);
    }
}
