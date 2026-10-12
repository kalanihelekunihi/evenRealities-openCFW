/* Native stack state-two handoff at 0x536608. */
#include <stdint.h>

extern void WsfMsgSend(uint8_t,void *);

void audio_ble_stack_state2_536608_body(uint8_t *message)
{
    uint32_t context_word;
    __builtin_memcpy(&context_word,message+0x30u,4u);
    uint8_t *context=(uint8_t *)(uintptr_t)context_word;
    uint32_t payload=(uint32_t)(uintptr_t)(message+16u);
    __builtin_memcpy(message+4u,&payload,4u);
    __builtin_memcpy(message+8u,context,4u);
    WsfMsgSend(context[0x28u],message);
}

__attribute__((naked)) uint32_t audio_ble_stack_state2_536608(
    uint8_t *message __attribute__((unused)))
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "bl audio_ble_stack_state2_536608_body\n"
        "pop {r0, pc}\n");
}
