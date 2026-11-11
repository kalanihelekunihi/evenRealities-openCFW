#include <stdint.h>

/* Native 0x329034..0x329064: slave BIG state machine step. Run the
 * optional action for (state, event) from the 4x5 table at 0x335460,
 * then load the next state (byte +1) from the byte table at 0x3354b0. */
extern const uintptr_t opencfw_em9305_slave_big_actions_335460[20];
extern const uint8_t opencfw_em9305_slave_big_transitions_3354b0[20];

uint32_t opencfw_em9305_child_329034(uintptr_t machine,uint32_t event)
{
    uint32_t state=*(volatile uint8_t *)(machine+1u);
    uintptr_t action=opencfw_em9305_slave_big_actions_335460[state*5u+event];
    if(action!=0u){
        (void)((uint32_t (*)(uintptr_t,uintptr_t,uint32_t))action)
            (machine,action,state);
        state=*(volatile uint8_t *)(machine+1u);
    }
    uint32_t next=opencfw_em9305_slave_big_transitions_3354b0[state*5u+event];
    *(volatile uint8_t *)(machine+1u)=(uint8_t)next;
    return next;
}
