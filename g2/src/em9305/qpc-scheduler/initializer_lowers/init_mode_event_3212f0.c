#include <stdint.h>

/* Complete native 0x3212f0..0x3213ae. The twelve-slot event callback
 * table at 0x803d28 is runtime data, read afresh for every slot. */
extern uint32_t opencfw_em9305_mode_event_323374(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_31c420(uintptr_t context,
                                                   uint32_t event);
uint32_t opencfw_em9305_mode_event_3212f0(uintptr_t context,
                                            uint32_t event)
{
    if (event==0x1cu && *(volatile uint8_t *)(context+526u)!=0u)
        return opencfw_em9305_mode_event_323374(context);
    for (uint32_t slot=0u;slot<12u;slot++) {
        uintptr_t address=0x803d28u+4u*slot;
        uintptr_t callback=*(volatile uint32_t *)address;
        if (callback!=0u) {
            uint32_t result=((uint32_t (*)(uintptr_t,uint32_t))callback)(
                context,event);
            if (result!=0u) return result;
        }
    }
    return opencfw_em9305_mode_event_31c420(context,event);
}
