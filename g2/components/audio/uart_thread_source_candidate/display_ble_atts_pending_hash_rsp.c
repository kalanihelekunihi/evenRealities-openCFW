/* Native attsCheckPendDbHashReadRsp 0x534dd8; pinned Cordio atts_main.c. */
#include <stdint.h>
extern uint8_t audio_ble_att_common_state[]; /* native attCb 0x200610ac */
extern uint8_t *attMsgAlloc(uint16_t length);
extern uint8_t *attsFindByHandle(uint16_t handle,void **group);
extern void attsErrRsp(uint8_t *ccb,uint8_t bearer,uint8_t opcode,
                       uint16_t handle,uint8_t error);
extern void L2cDataReq(uint16_t cid,uint16_t handle,uint16_t length,uint8_t *buffer);
extern void WsfBufFree(void *buffer);
static uint8_t *pointer_at(const uint8_t *p)
{
    uint32_t raw;
    __builtin_memcpy(&raw,p,4u);
    return (uint8_t *)(uintptr_t)raw;
}
static void put_pointer(uint8_t *p,uint8_t *value)
{
    uint32_t raw=(uint32_t)(uintptr_t)value;
    __builtin_memcpy(p,&raw,4u);
}
static uint16_t half_at(const uint8_t *p)
{
    return (uint16_t)p[0]|((uint16_t)p[1]<<8u);
}
void attsCheckPendDbHashReadRsp(void)
{
    for (uint8_t i=0u;i<3u;i++) {
        uint8_t *ccb=audio_ble_att_common_state+(uint32_t)i*0x14u;
        uint8_t *pending=pointer_at(ccb+0x10u);
        if (!pending) continue;
        const uint16_t start=half_at(pending);
        uint8_t *buffer=attMsgAlloc((uint16_t)(half_at(ccb)+8u));
        if (!buffer) {
            attsErrRsp(ccb,0u,8u,start,0x11u);
        } else {
            buffer[8u]=9u;
            buffer[9u]=0x12u;
            uint16_t handle=half_at(pending+2u);
            buffer[0x0au]=(uint8_t)handle;
            buffer[0x0bu]=(uint8_t)(handle>>8u);
            void *group=0;
            uint8_t *attribute=attsFindByHandle(handle,&group);
            if (!attribute) {
                attsErrRsp(ccb,0u,8u,start,0x0au);
            } else {
                const uint16_t value_length=half_at(pointer_at(attribute+8u));
                __builtin_memcpy(buffer+0x0cu,pointer_at(attribute+4u),value_length);
                L2cDataReq(4u,half_at(ccb+0x0cu),
                           (uint16_t)(value_length+4u),buffer);
            }
        }
        WsfBufFree(pending);
        put_pointer(ccb+0x10u,0);
    }
}
