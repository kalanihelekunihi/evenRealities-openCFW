/* Native BLE stack key/command callback 0x5366dc. */
#include <stdint.h>

extern void WStrReverseCpy(uint8_t *,const uint8_t *,uint16_t);
extern void WsfMsgSend(uint8_t,void *);

void audio_ble_stack_callback_5366dc(uint8_t *message,const uint8_t *event,
                                       uint8_t handler)
{
    if (event[2u]==0x25u) {
        WStrReverseCpy(message+4u,event+5u,32u);
        WStrReverseCpy(message+36u,event+37u,32u);
        message[3u]=event[4u];
        WsfMsgSend(handler,message);
    } else if (event[2u]==0x26u) {
        if (event[3u]==0x12u) {
            message[3u]=0x12u;
        } else {
            WStrReverseCpy(message+4u,event+5u,32u);
            message[3u]=event[4u];
        }
        WsfMsgSend(handler,message);
    }
}
