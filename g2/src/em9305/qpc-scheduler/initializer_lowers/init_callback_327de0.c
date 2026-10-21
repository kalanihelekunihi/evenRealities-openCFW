#include <stdint.h>

/* Native branch alias 0x327de0 -> 0x327fe4. The event's byte+3 is loaded
 * in the branch delay slot. Four states x five selectors are represented by
 * the ROM word table at 0x334b1c and byte table at 0x334b6c. */
extern const uintptr_t opencfw_em9305_init_transition_callbacks_334b1c[20];
extern const uint8_t opencfw_em9305_init_transition_states_334b6c[20];

uint32_t opencfw_em9305_init_callback_327de0(uintptr_t event,
                                               uint32_t incoming_r1,
                                               uint32_t incoming_r2,
                                               uintptr_t ambient_r3)
{
    (void)incoming_r1;
    (void)incoming_r2;
    uint32_t selector=*(volatile uint8_t *)(event+3u);
    uint32_t state=*(volatile uint8_t *)(uintptr_t)0x8052fbu;
    uint32_t byte_offset=state*20u+selector*4u;
    uintptr_t callback=opencfw_em9305_init_transition_callbacks_334b1c[byte_offset/4u];
    if(callback!=0u) {
        (void)((uint32_t (*)(uintptr_t,uint32_t,uint32_t,uintptr_t))callback)
            (callback,byte_offset,state,ambient_r3);
        state=*(volatile uint8_t *)(uintptr_t)0x8052fbu;
    }
    uint32_t next=opencfw_em9305_init_transition_states_334b6c[state*5u+selector];
    *(volatile uint8_t *)(uintptr_t)0x8052fbu=(uint8_t)next;
    return next;
}
