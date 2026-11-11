#include <stdint.h>

/* Native 0x31d0fc..0x31d126: dispatcher state machine step. The state byte
 * lives at object+1; each state row has eight events. Run the row's
 * callback (if any) on the object, then store and return the next state
 * from the transition table, indexed by the state re-read after the
 * callback. The stock call leaves the callback address in r1. */
extern const uintptr_t opencfw_em9305_dispatch_callbacks_334f70[];
extern const uint8_t opencfw_em9305_dispatch_transitions_335010[];

uint32_t opencfw_em9305_callback_child_31d0fc(uintptr_t object,uint32_t event)
{
    volatile uint8_t *state_slot=(volatile uint8_t *)(object+1u);
    uint32_t state = *state_slot;
    uintptr_t callback=opencfw_em9305_dispatch_callbacks_334f70[state*8u+event];
    if(callback!=0u) {
        ((void (*)(uintptr_t,uintptr_t))callback)(object,callback);
        state=*state_slot;
    }
    uint32_t next=opencfw_em9305_dispatch_transitions_335010[state*8u+event];
    *state_slot=(uint8_t)next;
    return next;
}
