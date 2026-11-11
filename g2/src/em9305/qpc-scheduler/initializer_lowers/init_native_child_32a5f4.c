#include <stdint.h>

/* Native 0x32a5f4..0x32a626: encryption state machine step. The state
 * byte at +621 and the event select a row of the 7x7 action/transition
 * tables at 0x335564/0x335628; the action (if any) runs with the record,
 * its own address and the state, then the next state is stored. */
extern void (*const opencfw_em9305_enc_actions_335564[49])(void);
extern const uint8_t opencfw_em9305_enc_transitions_335628[49];

void opencfw_em9305_child_32a5f4(uintptr_t record, uint32_t event)
{
    volatile uint8_t *state=(volatile uint8_t *)(record+621u);
    uint32_t current=*state;
    uintptr_t action=(uintptr_t)opencfw_em9305_enc_actions_335564[current*7u+event];
    if(action!=0u){
        ((void (*)(uintptr_t,uintptr_t,uint32_t))action)(record,action,current);
        current=*state;
    }
    *state=opencfw_em9305_enc_transitions_335628[current*7u+event];
}
