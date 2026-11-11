#include <stdint.h>

/* Native 0x31fa10..0x31fa42: master encryption state machine step. The
 * state byte lives at record+621; each state row has seven events. Run the
 * row's action (if any) on the record, then store and return the next
 * state from the transition table (indexed by the state re-read after the
 * action). The stock call leaves the action address in r1. */
extern const uintptr_t opencfw_em9305_mst_enc_actions_335114[];
extern const uint8_t opencfw_em9305_mst_enc_transitions_3351f4[];

uint32_t opencfw_em9305_child_31fa10(uintptr_t record,uint32_t event)
{
    volatile uint8_t *state_slot=(volatile uint8_t *)(record+621u);
    uint32_t state = *state_slot;
    uintptr_t action=opencfw_em9305_mst_enc_actions_335114[state*7u+event];
    if(action!=0u) {
        ((void (*)(uintptr_t,uintptr_t))action)(record,action);
        state=*state_slot;
    }
    uint32_t next=opencfw_em9305_mst_enc_transitions_3351f4[state*7u+event];
    *state_slot=(uint8_t)next;
    return next;
}
