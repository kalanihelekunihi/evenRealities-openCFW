/* Native 0x536620 dispatches a copied 16-byte stack segment by the
 * context state byte at +0x29. Its three exact native children remain
 * separately named callable contracts pending their connected reduction. */
#include <stdint.h>

extern void audio_ble_stack_copy16_542a44(void *,const void *);
extern void audio_ble_stack_state0_5365a6(uint8_t *);
extern void audio_ble_stack_state1_5364a4(uint8_t *);
extern void audio_ble_stack_state2_536608(uint8_t *);

void audio_ble_stack_callback_536620_body(uint8_t *message,const uint8_t *payload)
{
    uint32_t context_word;
    __builtin_memcpy(&context_word,message+0x30u,4u);
    if (context_word==0u) return;
    uint8_t *context=(uint8_t *)(uintptr_t)context_word;
    audio_ble_stack_copy16_542a44(message+16u,payload+5u);
    switch (context[0x29u]) {
    case 0u: audio_ble_stack_state0_5365a6(message); break;
    case 1u: audio_ble_stack_state1_5364a4(message); break;
    case 2u: audio_ble_stack_state2_536608(message); break;
    default: break;
    }
}

__attribute__((naked)) uint32_t audio_ble_stack_callback_536620(
    uint8_t *message __attribute__((unused)),const uint8_t *payload __attribute__((unused)),
    uint32_t unused __attribute__((unused)),uint32_t inherited __attribute__((unused)))
{
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "bl audio_ble_stack_callback_536620_body\n"
        "pop {r0, r4, r5, pc}\n");
}
