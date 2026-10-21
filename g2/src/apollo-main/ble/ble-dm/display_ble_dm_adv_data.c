/* Pinned Cordio dm_adv.c DmAdvSetData, native Main 0x4b319e. */
#include <stdint.h>
extern uint8_t audio_ble_dm_handler_state[]; /* native dmCb 0x20073b78 */
extern uint8_t *WsfMsgAlloc(uint16_t length);
extern void WsfMsgSend(uint8_t handler,void *message);
void DmAdvSetData(uint8_t handle,uint8_t operation,uint8_t location,
                  uint8_t length,const uint8_t *data)
{
    uint8_t *message=WsfMsgAlloc((uint16_t)length+8u);
    if (!message) return;
    message[2u]=1u;
    message[4u]=handle;
    message[5u]=operation;
    message[6u]=location;
    message[7u]=length;
    for (uint32_t i=0u;i<length;i++) message[8u+i]=data[i];
    WsfMsgSend(audio_ble_dm_handler_state[0x0cu],message);
}
