#include <stdint.h>

/* Native 0x31ff2c..0x31ff68: release a finished command. Releases common
 * resource 1, counts down the init state for command states 1, 3 and 4
 * (+98), frees the pending event at +392, and decrements the outstanding
 * command count at 0x805a74. */
extern uint32_t opencfw_em9305_common_release_304588(uint32_t resource);
extern uint32_t opencfw_em9305_init_state_count_down_30e49c(void);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t event);
extern uint32_t opencfw_em9305_command_count_down_30e48c(void);

uint32_t opencfw_em9305_child_31ff2c(uintptr_t command)
{
    (void)opencfw_em9305_common_release_304588(1u);
    uint32_t state=*(volatile uint8_t *)(command+98u);
    if(state<5u&&((0x1au>>state)&1u)!=0u)
        (void)opencfw_em9305_init_state_count_down_30e49c();
    uintptr_t event=*(volatile uint32_t *)(command+392u);
    if(event!=0u){
        (void)opencfw_em9305_wsf_event_release(event);
        *(volatile uint32_t *)(command+392u)=0u;
    }
    volatile uint8_t *count=(volatile uint8_t *)(uintptr_t)0x805a74u;
    *count=(uint8_t)(*count-1u);
    return opencfw_em9305_command_count_down_30e48c();
}
