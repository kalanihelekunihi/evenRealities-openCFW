/* Pinned Cordio app_slave_leg.c/app_slave.c advertising data setters,
 * native Main 0x4b2cec and 0x4b4240. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern int appSlaveAdvMode(void);
extern void appSetAdvScanDataFrag(uint8_t handle,uint8_t location);
static void set16(uint8_t *p,uint16_t v) { p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u); }
static void set32(uint8_t *p,uint32_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u);
    p[2]=(uint8_t)(v>>16u);p[3]=(uint8_t)(v>>24u);
}

__attribute__((noinline)) void appAdvSetData(uint8_t handle,uint8_t location,uint16_t length,
                   const uint8_t *data,uint16_t maximum_fragment,
                   uint16_t maximum_data)
{
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    uint32_t index=(uint32_t)handle*8u+(uint32_t)location*2u;
    set32(state+(uint32_t)handle*0x10u+(uint32_t)location*4u,(uint32_t)(uintptr_t)data);
    set16(state+0x20u+index,length);
    set16(state+0x30u+index,maximum_fragment);
    set16(state+0x50u+(uint32_t)handle*2u,maximum_data);
    set16(state+0x40u+index,0u);
    if (state[0x57u+handle]==3u || (location>>1u)!=state[0x5du] ||
        length>0xfbu || maximum_data<length)
        state[0x55u+handle]=0u;
    else
        appSetAdvScanDataFrag(handle,location);
}

void AppAdvSetData(uint8_t location,uint8_t length,const uint8_t *data)
{
    if (!appSlaveAdvMode()) return;
    if (length>0x1fu) length=0x1fu;
    appAdvSetData(0u,location,length,data,0x1fu,0x1fu);
}
