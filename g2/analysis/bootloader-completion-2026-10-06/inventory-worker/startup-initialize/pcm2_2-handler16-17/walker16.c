/* SPDX-License-Identifier: MIT
 * Source wrapper for the locked temperature transition walker when a
 * selector16 handler is installed. It preserves the walker's saved-r2/r3
 * return words as selector-id/original-r3, and dispatches through the
 * authenticated runtime callback table.
 */
#include <stdint.h>
typedef uint32_t (*callback_t)(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t event_a_state_transition_sequence(uint32_t,uint32_t,uint8_t *);
#define CALLBACKS ((volatile callback_t *)(uintptr_t)0x20000158u)
uint64_t opencfw_spot_selector16_walker(uint32_t target_state,
                                       uint32_t current_state,
                                       uint32_t target_ton,
                                       uint32_t current_ton)
{
    uint8_t selector=26;
    uint32_t start,end;
    if(target_state>current_state){
        for(start=current_state;start<target_state;++start){
            end=start+1u;
            if(event_a_state_transition_sequence(end,start,&selector)==0u)
                (void)CALLBACKS[selector](target_state,current_state,target_ton,current_ton);
        }
    }else{
        for(start=current_state;start>target_state;--start){
            end=start-1u;
            if(event_a_state_transition_sequence(end,start,&selector)==0u)
                (void)CALLBACKS[selector](target_state,current_state,target_ton,current_ton);
        }
    }
    /* Original walker stores selector in the saved-r2 slot and restores its
       saved-r3 argument as r1. */
    return ((uint64_t)current_ton<<32)|selector;
}
