#include <stdint.h>
extern uint32_t opencfw_em9305_command_count_down_30e48c(void);
extern uint32_t opencfw_em9305_init_state_count_down_30e49c(void);
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
uint32_t opencfw_em9305_init_transition_gate_3168e4(void);
extern uintptr_t opencfw_em9305_init_transition_refresh_327dbc(void);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);
extern uint32_t opencfw_em9305_init_secondary_count_up_30e4cc(void);
extern uint32_t opencfw_em9305_init_transition_start_327b60(void);
extern uint32_t opencfw_em9305_init_state_count_down_30e49c(void);

/* Native 0x3168e4..0x316904, shared by two selector callbacks. */
uint32_t opencfw_em9305_init_transition_gate_3168e4(void)
{
    (void)opencfw_em9305_command_count_down_30e48c();
    uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x805b9du;
    *(volatile uint8_t *)(uintptr_t)0x805a71u=0u;
    if(enabled!=0u)return opencfw_em9305_init_state_count_down_30e49c();
    return 0u;
}
uint32_t opencfw_em9305_init_transition_count_down_320068(void)
{
    (void)opencfw_em9305_common_release_304588(1u);
    uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805a74u;
    *(volatile uint8_t *)(uintptr_t)0x805a74u=(uint8_t)(count-1u);
    return opencfw_em9305_command_count_down_30e48c();
}
