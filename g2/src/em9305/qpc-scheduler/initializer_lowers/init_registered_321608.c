#include <stdint.h>

/* Native 0x321608..0x321644 and its connected 0x3217f0..0x32181e
 * transition child. 0x335398 has four states x five selectors of callback
 * identities; 0x3353e8 has the corresponding one-byte next states. */
extern const uintptr_t opencfw_em9305_init_transition_callbacks_335398[20];
extern const uint8_t opencfw_em9305_init_transition_states_3353e8[20];

static uint32_t opencfw_em9305_init_transition_3217f0(uintptr_t row,
                                                        uint32_t selector)
{
    uint32_t state=*(volatile uint8_t *)(row+1u);
    uint32_t index=state*5u+selector;
    uintptr_t callback=opencfw_em9305_init_transition_callbacks_335398[index];
    if(callback!=0u) {
        (void)((uint32_t (*)(uintptr_t,uintptr_t,uint32_t))callback)
            (row,callback,state);
        state=*(volatile uint8_t *)(row+1u);
    }
    uint32_t next=opencfw_em9305_init_transition_states_3353e8[state*5u+selector];
    *(volatile uint8_t *)(row+1u)=(uint8_t)next;
    return next;
}

uint32_t opencfw_em9305_init_registered_321608(uintptr_t event)
{
    *(volatile uint32_t *)(uintptr_t)0x805c80u=(uint32_t)event;
    uintptr_t row=0x803d78u;
    uint32_t kind=*(volatile uint8_t *)(event+2u);
    if(kind!=255u) {
        uint32_t index=*(volatile uint16_t *)event;
        uint32_t selector=*(volatile uint8_t *)(event+3u);
        return opencfw_em9305_init_transition_3217f0(row+index*784u,
                                                        selector);
    }
    uint32_t result=0u;
    for(uint32_t index=0u;index<6u;++index,row+=784u) {
        uint32_t selector=*(volatile uint8_t *)(event+3u);
        result=opencfw_em9305_init_transition_3217f0(row,selector);
    }
    return result;
}
