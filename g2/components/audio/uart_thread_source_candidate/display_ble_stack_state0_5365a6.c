/* Native stack state-zero transition 0x5365a6 and 16-byte left-shift
 * helper 0x53655c, retaining the selected copy child and state-one path. */
#include <stdint.h>

extern void audio_ble_stack_copy16_542a44(void *,const void *);
extern void audio_ble_stack_state1_5364a4(uint8_t *);

uint8_t audio_ble_stack_shift1_53655c(uint8_t *bytes,uint32_t bits)
{
    uint8_t carry=(uint8_t)(bytes[0]>>(8u-bits));
    for (uint32_t i=0u;i<16u;++i) {
        uint8_t next=i<15u ? bytes[i+1u] : 0u;
        bytes[i]=(uint8_t)((bytes[i]<<bits)|(next>>(8u-bits)));
    }
    return carry;
}

void audio_ble_stack_state0_5365a6_body(uint8_t *message)
{
    uint32_t context_word;
    __builtin_memcpy(&context_word,message+0x30u,4u);
    uint8_t *context=(uint8_t *)(uintptr_t)context_word;
    audio_ble_stack_copy16_542a44(context+0x14u,message+16u);
    if (audio_ble_stack_shift1_53655c(context+0x14u,1u)!=0u)
        context[0x23u]^=0x87u;
    if ((context[0x26u]&15u)!=0u &&
        audio_ble_stack_shift1_53655c(context+0x14u,1u)!=0u)
        context[0x23u]^=0x87u;
    context[0x29u]=1u;
    audio_ble_stack_state1_5364a4(message);
}

__attribute__((naked)) uint32_t audio_ble_stack_state0_5365a6(
    uint8_t *message __attribute__((unused)))
{
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "bl audio_ble_stack_state0_5365a6_body\n"
        "pop {r0, r4, r5, pc}\n");
}
