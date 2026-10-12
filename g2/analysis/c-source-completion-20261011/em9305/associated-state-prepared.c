extern uint32_t opencfw_em9305_associated_action_32b5ec(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_event_32b4e4(uintptr_t);
/* Native30a328..30a378. Return retains native incidental R0. */
uint32_t opencfw_em9305_init_lower_30a328(uint32_t incoming)
{
 (void)incoming;uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(config+4u);
 *(volatile uint32_t *)(uintptr_t)0x802978u=(uint32_t)(uintptr_t)opencfw_em9305_associated_event_32b4e4;
 *(volatile uint32_t *)(uintptr_t)0x801310u=(uint32_t)(uintptr_t)opencfw_em9305_radio_record_available_307410;
 *(volatile uint32_t *)(uintptr_t)0x805224u=0u;
 if(version<9u)return (uint32_t)config;
 uint32_t flags=*(volatile uint32_t *)(uintptr_t)0x805b30u;flags|=1u<<13u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=flags;
 if(version<12u)return flags;
 uint32_t second=*(volatile uint32_t *)(uintptr_t)0x805b34u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=flags;
 *(volatile uint32_t *)(uintptr_t)0x805b34u=second|(1u<<4u);
 return flags;
}
/* Native32b4e4..32b536: event over one or every active2824B associated row. */
uint32_t opencfw_em9305_associated_event_32b4e4(uintptr_t event)
{
 *(volatile uint32_t *)(uintptr_t)0x805cc0u=(uint32_t)event;
 if(*(volatile uint8_t *)(event+2u)!=255u){
  uintptr_t record=opencfw_em9305_radio_record_find_31aa64(*(volatile uint8_t *)event);
  if(record==0u)return 0u;
  return opencfw_em9305_associated_action_32b5ec(record,*(volatile uint8_t *)(event+3u));
 }
 uint32_t number=0u,offset=0u;
 for(;;){
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t count=*(volatile uint8_t *)(config+12u);
  if(number>=count)return count;
  uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c38u;record+=offset;
  if(*(volatile uint8_t *)record!=0u)(void)opencfw_em9305_associated_action_32b5ec(record,*(volatile uint8_t *)(event+3u));
  offset+=2824u;number++;
 }
}
extern uint32_t opencfw_em9305_associated_action_324b3c(uintptr_t);
extern uint32_t opencfw_em9305_associated_action_324c60(uintptr_t);
extern uint32_t opencfw_em9305_associated_action_324aa8(uintptr_t);
extern uint32_t opencfw_em9305_associated_action_324aa0(uintptr_t);
extern uint32_t opencfw_em9305_associated_action_324a8c(uintptr_t);
typedef uint32_t (*opencfw_em9305_associated_action_fn)(uintptr_t);
const opencfw_em9305_associated_action_fn opencfw_em9305_associated_actions_335328[16]={
0,opencfw_em9305_associated_action_324b3c,0,0,0,opencfw_em9305_associated_action_324c60,opencfw_em9305_associated_action_324aa8,0,0,opencfw_em9305_associated_action_324aa0,opencfw_em9305_associated_action_324aa0,opencfw_em9305_associated_action_324a8c,0,opencfw_em9305_associated_action_324aa0,opencfw_em9305_associated_action_324aa0,0
};
const uint8_t opencfw_em9305_associated_transitions_335368[16]={0u,1u,0u,0u,3u,1u,2u,0u,3u,2u,2u,0u,3u,3u,3u,0u};
/* Native32b5ec..32b614: callback-mutated state is reloaded before transition. */
uint32_t opencfw_em9305_associated_action_32b5ec(uintptr_t record,uint32_t action)
{
 uint32_t state=*(volatile uint8_t *)(record+368u);
 opencfw_em9305_associated_action_fn callback=opencfw_em9305_associated_actions_335328[state*4u+action];
 if(callback!=0){(void)callback(record);state=*(volatile uint8_t *)(record+368u);}
 uint32_t next=opencfw_em9305_associated_transitions_335368[state*4u+action];
 *(volatile uint8_t *)(record+368u)=(uint8_t)next;return next;
}
