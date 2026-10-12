/* Pinned Cordio dm_adv.c DmAdvStop, native Main 0x4b3250. */
#include <stdint.h>
extern uint8_t audio_ble_dm_handler_state[]; /* native dmCb 0x20073b78 */
extern uint8_t *WsfMsgAlloc(uint16_t length);
extern void WsfMsgSend(uint8_t handler,void *message);
void DmAdvStop(uint8_t number_of_sets,const uint8_t *handles)
{
    uint8_t *message=WsfMsgAlloc(8u);
    if (!message) return;
    message[2u]=3u;
    message[4u]=number_of_sets;
    for (uint8_t i=0u;i<number_of_sets;i++) message[5u+i]=handles[i];
    WsfMsgSend(audio_ble_dm_handler_state[0x0cu],message);
}
