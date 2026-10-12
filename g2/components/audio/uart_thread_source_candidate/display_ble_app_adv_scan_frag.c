/* Pinned Cordio app_slave.c fragment emitter, native Main 0x4b3416. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern void DmAdvSetData(uint8_t handle,uint8_t operation,uint8_t location,
                         uint8_t length,const uint8_t *data);
static uint16_t get16(const uint8_t *p) { return (uint16_t)p[0]|((uint16_t)p[1]<<8u); }
static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|
           ((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);
}
static void set16(uint8_t *p,uint16_t v) { p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u); }
void appSetAdvScanDataFrag(uint8_t handle,uint8_t location)
{
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    uint32_t index=(uint32_t)handle*8u+(uint32_t)location*2u;
    uint8_t *const offset_cell=state+0x40u+index;
    uint16_t offset=get16(offset_cell);
    uint16_t remain=(uint16_t)(get16(state+0x20u+index)-offset);
    uint16_t maximum=get16(state+0x50u+(uint32_t)handle*2u);
    if (remain>maximum) remain=maximum;
    const uint8_t *const data=(const uint8_t *)(uintptr_t)
        get32(state+(uint32_t)handle*0x10u+(uint32_t)location*4u);
    uint8_t first=1u;
    while (remain) {
        uint16_t fragment=remain>0xfbu?0xfbu:remain;
        uint8_t operation=remain>0xfbu ? (first?1u:0u) : (first?3u:2u);
        DmAdvSetData(handle,operation,location&1u,(uint8_t)fragment,data+offset);
        offset=(uint16_t)(offset+fragment);
        set16(offset_cell,offset);
        remain=(uint16_t)(remain-fragment);
        first=0u;
    }
}
