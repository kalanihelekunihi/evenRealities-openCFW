/* Native334f20: genuine four-state/four-event action identities.
 * These actions ignore incoming R2/R3, confirmed from their full native CFG.
 * Loaded action address R0 and captured state R1 retain native call ABI. */
typedef uint32_t (*opencfw_em9305_init_state_action)(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_state_action_31b4e0(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_state_action_31b4a4(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_state_action_31b6b0(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_state_action_31b4c8(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_state_action_31b3b8(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_state_action_31b648(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_state_action_31b614(uintptr_t,uint32_t);
static opencfw_em9305_init_state_action const opencfw_em9305_init_state_actions_334f20[16]={
 0,opencfw_em9305_init_state_action_31b4e0,opencfw_em9305_init_state_action_31b4a4,0,
 opencfw_em9305_init_state_action_31b6b0,opencfw_em9305_init_state_action_31b4c8,opencfw_em9305_init_state_action_31b6b0,opencfw_em9305_init_state_action_31b3b8,
 0,opencfw_em9305_init_state_action_31b4c8,0,opencfw_em9305_init_state_action_31b648,
 0,opencfw_em9305_init_state_action_31b4c8,opencfw_em9305_init_state_action_31b4a4,opencfw_em9305_init_state_action_31b614};
static const uint8_t opencfw_em9305_init_state_transitions_334f60[16]={0,1,0,0,3,1,2,0,3,2,2,0,3,3,3,0};
/* Native320580..3205b2: event byte3, captured state then fresh post-action state.
 * Out-of-range event/state remains unqualified; no invented native guard. */
uint32_t opencfw_em9305_init_state_event_320580(uintptr_t event)
{
 uint32_t index=*(volatile uint8_t *)(event+3u);
 uint32_t state=*(volatile uint8_t *)(uintptr_t)0x803bb8u;
 opencfw_em9305_init_state_action action=opencfw_em9305_init_state_actions_334f20[state*4u+index];
 if(action!=0){(void)action((uintptr_t)action,state);state=*(volatile uint8_t *)(uintptr_t)0x803bb8u;}
 uint32_t next=opencfw_em9305_init_state_transitions_334f60[index+4u*state];
 *(volatile uint8_t *)(uintptr_t)0x803bb8u=(uint8_t)next;return next;
}
/* Native3205b4..3205c0: genuine reset, full404-byte memset tail. */
uint32_t opencfw_em9305_init_state_reset_3205b4(void)
{return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)(uintptr_t)0x803b94u,0u,404u);}
/* Native307bdc..307c04: typed callback registrations and reset body. */
uint32_t opencfw_em9305_init_lower_307bdc(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x80295cu=(uint32_t)(uintptr_t)opencfw_em9305_init_state_event_320580;
 *(volatile uint32_t *)(uintptr_t)0x805208u=(uint32_t)(uintptr_t)opencfw_em9305_init_state_reset_3205b4;
 return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)(uintptr_t)0x803b94u,0u,404u);
}
