/* Native attMsgAlloc 0x4b50ae, attsErrRsp 0x534c9a,
 * attsFindByHandle 0x56c5d4; pinned Cordio ATT sources. */
#include <stdint.h>
extern uint8_t audio_ble_atts_state[]; /* native attsCb 0x2006e5f0 */
extern uint8_t *WsfMsgDataAlloc(uint16_t length,uint8_t offset);
extern void attL2cDataReq(uint8_t *ccb,uint8_t slot,uint16_t length,uint8_t *packet);

uint8_t *attMsgAlloc(uint16_t length)
{
    return WsfMsgDataAlloc(length,0u);
}

void attsErrRsp(uint8_t *ccb,uint8_t slot,uint8_t opcode,
                uint16_t handle,uint8_t error)
{
    uint8_t *message=attMsgAlloc(0x0du);
    if (!message) return;
    message[8u]=1u;
    message[9u]=opcode;
    message[0x0au]=(uint8_t)handle;
    message[0x0bu]=(uint8_t)(handle>>8u);
    message[0x0cu]=error;
    attL2cDataReq(ccb,slot,5u,message);
}

uint8_t *attsFindByHandle(uint16_t handle,void **group_out)
{
    uint32_t raw;
    __builtin_memcpy(&raw,audio_ble_atts_state+0x258u,4u);
    uint8_t *group=(uint8_t *)(uintptr_t)raw;
    while (group) {
        uint16_t first=(uint16_t)group[0x10u]|((uint16_t)group[0x11u]<<8u);
        uint16_t last=(uint16_t)group[0x12u]|((uint16_t)group[0x13u]<<8u);
        if (first<=handle && handle<=last) {
            *group_out=group;
            __builtin_memcpy(&raw,group+4u,4u);
            return (uint8_t *)(uintptr_t)raw+(uint32_t)(handle-first)*0x10u;
        }
        __builtin_memcpy(&raw,group,4u);
        group=(uint8_t *)(uintptr_t)raw;
    }
    return 0;
}
