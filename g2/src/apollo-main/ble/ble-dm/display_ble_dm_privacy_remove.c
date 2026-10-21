/* Native DmHostAddrType 0x4d2aa8 and DmPrivRemDevFromResList 0x4d2880. */
#include <stdint.h>
extern uint8_t audio_ble_dm_handler_state[0x18u]; /* live product struct 0x20073b78 */
extern void *WsfMsgAlloc(uint16_t);
extern void WsfMsgSend(uint8_t,void *);
uint8_t DmHostAddrType(uint8_t type) {
    if(audio_ble_dm_handler_state[0x16u]) {
        if(type==2u)return 0u;
        if(type==3u)return 1u;
    }
    return type;
}
void DmPrivRemDevFromResList(uint8_t type,const uint8_t *address,uint16_t handle) {
    uint8_t *message=(uint8_t *)WsfMsgAlloc(12u);
    if(!message)return;
    message[0]=(uint8_t)handle;
    message[1]=(uint8_t)(handle>>8u);
    message[2]=0x32u;
    message[4]=type;
    for(uint32_t i=0u;i<6u;i++)message[5u+i]=address[i];
    WsfMsgSend(audio_ble_dm_handler_state[0x0cu],message);
}
