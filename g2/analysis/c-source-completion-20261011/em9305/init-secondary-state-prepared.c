/* Native334cac: four state rows, six event columns, typed source identities.
 * Observed callback inputs R0=callee,R1=24*state+4*event,R2=state;
 * ambient higher-register ABI remains explicitly unqualified. */
typedef uint32_t (*opencfw_em9305_init_secondary_action)(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_secondary_action_318fc0(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_secondary_action_318fe8(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_secondary_action_319080(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_secondary_action_319094(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_secondary_action_3190e0(uintptr_t,uint32_t,uint32_t);
const opencfw_em9305_init_secondary_action opencfw_em9305_init_secondary_actions_334cac[24]={
0,opencfw_em9305_init_secondary_action_318fe8,0,0,0,0,opencfw_em9305_init_secondary_action_318fc0,0,opencfw_em9305_init_secondary_action_318fc0,opencfw_em9305_init_secondary_action_319094,opencfw_em9305_init_secondary_action_319080,0,0,0,0,0,0,opencfw_em9305_init_secondary_action_3190e0,0,0,0,0,0,opencfw_em9305_init_secondary_action_3190e0};
const uint8_t opencfw_em9305_init_secondary_transitions_335790[24]={0u,1u,0u,0u,0u,0u,3u,1u,2u,2u,0u,1u,2u,2u,2u,2u,2u,0u,3u,3u,3u,3u,0u,0u};
/* Complete native31e90c..31e93c. Fresh state is read after action. */
uint32_t opencfw_em9305_init_secondary_dispatch_31e90c(uint32_t event)
{
 uint32_t state=*(volatile uint8_t *)(uintptr_t)0x8051a4u;
 opencfw_em9305_init_secondary_action action=opencfw_em9305_init_secondary_actions_334cac[state*6u+event];
 if(action!=0){(void)action((uintptr_t)action,state*24u+event*4u,state);state=*(volatile uint8_t *)(uintptr_t)0x8051a4u;}
 uint32_t next=opencfw_em9305_init_secondary_transitions_335790[state*6u+event];
 *(volatile uint8_t *)(uintptr_t)0x8051a4u=(uint8_t)next;
 return next;
}
/* Complete native31e8fc..31e908 dispatch entry. */
uint32_t opencfw_em9305_init_registered_31e8fc(uintptr_t message)
{
 *(volatile uint32_t *)(uintptr_t)0x805c80u=(uint32_t)message;
 uint32_t event=*(volatile uint8_t *)(message+3u);
 return opencfw_em9305_init_secondary_dispatch_31e90c(event);
}
/* Complete native319080..31908e clearing return preserves prior byte. */
uint32_t opencfw_em9305_init_secondary_action_319080(uintptr_t incoming,uint32_t offset,uint32_t state)
{
 (void)incoming;(void)offset;(void)state;
 uint32_t prior=*(volatile uint8_t *)(uintptr_t)0x8051a5u;
 if(prior!=0u)*(volatile uint8_t *)(uintptr_t)0x8051a5u=0u;
 return prior;
}
