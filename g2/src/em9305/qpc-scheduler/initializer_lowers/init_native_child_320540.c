#include <stdint.h>

/* Native 0x320540..0x32056a: extended-scan state machine step. Run the
 * optional action for (state, event) from the 4x4 table at 0x334ed0, then
 * load the next state from the byte table at 0x334f10. */
extern const uintptr_t opencfw_em9305_ext_scan_actions_334ed0[16];
extern const uint8_t opencfw_em9305_ext_scan_transitions_334f10[16];

uint32_t opencfw_em9305_child_320540(uintptr_t machine,uint32_t event)
{
    uint32_t state=*(volatile uint8_t *)machine;
    uintptr_t action=opencfw_em9305_ext_scan_actions_334ed0[state*4u+event];
    if(action!=0u){
        (void)((uint32_t (*)(uintptr_t,uintptr_t,uint32_t))action)
            (machine,action,state);
        state=*(volatile uint8_t *)machine;
    }
    uint32_t next=opencfw_em9305_ext_scan_transitions_334f10[state*4u+event];
    *(volatile uint8_t *)machine=(uint8_t)next;
    return next;
}
