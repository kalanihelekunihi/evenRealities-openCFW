/* Pinned Cordio dm_adv.c DmAdvConfig, native Main 0x4b3166. */
#include <stdint.h>
extern uint8_t audio_ble_dm_handler_state[]; /* native dmCb 0x20073b78 */
extern uint8_t *WsfMsgAlloc(uint16_t length);
extern void WsfMsgSend(uint8_t handler,void *message);
void DmAdvConfig(uint8_t handle,uint8_t type,uint8_t peer_type,const uint8_t *peer_address)
{
    uint8_t *message=WsfMsgAlloc(0x0eu);
    if (!message) return;
    message[2u]=0u;
    message[4u]=handle;
    message[5u]=type;
    message[6u]=peer_type;
    for (uint8_t i=0u;i<6u;i++) message[7u+i]=peer_address[i];
    WsfMsgSend(audio_ble_dm_handler_state[0x0cu],message);
}
