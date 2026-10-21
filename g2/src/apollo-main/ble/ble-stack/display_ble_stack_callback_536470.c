/* Native BLE stack callback 0x536470 and its exact 16-byte copy child
 * 0x542a44, using the already selected 0x439be4 copy provider. */
#include <stdint.h>

extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern void WsfMsgSend(uint8_t,void *);

void audio_ble_stack_copy16_542a44(void *destination,const void *source)
{
    (void)audio_queue_copy_bytes(destination,source,16u);
}

void audio_ble_stack_callback_536470_body(uint8_t *message,const uint8_t *payload,
                                           uint8_t handler)
{
    uint32_t pointer=(uint32_t)(uintptr_t)(message+16u);
    __builtin_memcpy(message+4u,&pointer,4u);
    audio_ble_stack_copy16_542a44(message+16u,payload+5u);
    WsfMsgSend(handler,message);
}

/* Native saved fourth argument returns in R0 via pop {r0,r4,r5,pc}. */
__attribute__((naked)) uint32_t audio_ble_stack_callback_536470(
    uint8_t *message __attribute__((unused)),const uint8_t *payload __attribute__((unused)),
    uint8_t handler __attribute__((unused)),uint32_t inherited __attribute__((unused)))
{
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "bl audio_ble_stack_callback_536470_body\n"
        "pop {r0, r4, r5, pc}\n");
}
