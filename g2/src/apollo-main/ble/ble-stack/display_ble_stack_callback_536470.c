/* Native BLE stack callback 0x536470 and its exact 16-byte copy child
 * 0x542a44, using the already selected 0x439be4 copy provider. */
#include <stdint.h>

extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern void WsfMsgSend(uint8_t,void *);

extern void audio_ble_stack_copy16_542a44(void *destination,const void *source); /* opencfw U5: now provided by the Cordio unit */

void audio_ble_stack_callback_536470_body(uint8_t *message,const uint8_t *payload,
                                           uint8_t handler)
{
    uint32_t pointer=(uint32_t)(uintptr_t)(message+16u);
    __builtin_memcpy(message+4u,&pointer,4u);
    audio_ble_stack_copy16_542a44(message+16u,payload+5u);
    WsfMsgSend(handler,message);
}

