extern const opencfw_em9305_phy_action_fn opencfw_em9305_slave_phy_actions_33565c[];
extern const uint8_t opencfw_em9305_slave_phy_transitions_335704[];
/* Native32b04c..32b20e complete slave PHY state machine. */
uint32_t opencfw_em9305_init_slave_phy_state_32b04c(uintptr_t record,uint32_t event)
{
 uint32_t action=0u,force=0u;
 if((int32_t)event>=62){
  if(event==62u){action=6u;if(*(volatile uint8_t *)(record+635u)!=21u)return 0u;}
  else if(event==110u){action=4u;if(*(volatile uint8_t *)(record+635u)!=21u)return 0u;}
  else if(event==112u){
   uint32_t bits=*(volatile uint32_t *)(record+644u),extra=*(volatile uint32_t *)(record+648u);
   if((bits^(1u<<21u))!=0u||extra!=0u)return 0u;
   action=5u;*(volatile uint32_t *)(record+648u)=0u;*(volatile uint32_t *)(record+644u)=0u;
  }else return 0u;
 }else if(event==12u){
  uint32_t operation=*(volatile uint8_t *)(uintptr_t)0x802818u;
  if(operation==7u||operation==17u){action=3u;if(*(volatile uint8_t *)(uintptr_t)0x80281cu!=22u)return 0u;}
  else if(operation==13u){action=3u;if(*(volatile uint8_t *)(record+635u)!=21u)return 0u;}
  else if(operation==22u){action=2u;force=1u;}
  else if(operation==24u)action=1u;
  else return 0u;
 }else if(event!=32u)return 0u;
 uint32_t active=*(volatile uint8_t *)(record+620u);
 if(active==0u){
  uint32_t state=*(volatile uint8_t *)(record+625u);
  opencfw_em9305_phy_action_fn callback=opencfw_em9305_slave_phy_actions_33565c[state*7u+action];
  if(callback!=0){(void)callback(record);state=*(volatile uint8_t *)(record+625u);}
  uint32_t next=opencfw_em9305_slave_phy_transitions_335704[state*7u+action];
  *(volatile uint8_t *)(record+625u)=(uint8_t)next;
  *(volatile uint8_t *)(record+634u)=(uint8_t)(next==5u);
  if(next!=0u){*(volatile uint8_t *)(record+620u)=1u;*(volatile uint8_t *)(record+635u)=21u;*(volatile uint8_t *)(record+628u)=0u;}
  return 1u;
 }
 if(active!=1u)return 1u;
 uint32_t procedure=*(volatile uint8_t *)(record+635u);
 if(force!=0u){
  if(procedure-2u>=3u&&procedure!=21u&&procedure!=7u)goto deferred;
  if(procedure!=21u){
   uint32_t bits=*(volatile uint32_t *)(record+644u);
   *(volatile uint8_t *)(record+635u)=21u;*(volatile uint8_t *)(record+631u)=1u;
   *(volatile uint32_t *)(record+644u)=bits|(1u<<(procedure&31u));
  }
 }else if(procedure!=21u)goto deferred;
 {
  uint32_t state=*(volatile uint8_t *)(record+625u);
  opencfw_em9305_phy_action_fn callback=opencfw_em9305_slave_phy_actions_33565c[state*7u+action];
  if(callback!=0){(void)callback(record);state=*(volatile uint8_t *)(record+625u);}
  uint32_t next=opencfw_em9305_slave_phy_transitions_335704[state*7u+action];
  *(volatile uint8_t *)(record+625u)=(uint8_t)next;
  *(volatile uint8_t *)(record+634u)=(uint8_t)(next==5u);
  if(next==0u){(void)opencfw_em9305_phy_complete_32c818(record);*(volatile uint8_t *)(record+635u)=255u;*(volatile uint8_t *)(record+620u)=0u;(void)opencfw_em9305_phy_finish_32c810(record);}
  return 1u;
 }
 deferred:
 if(action==0u){
  (void)opencfw_em9305_phy_defer_32caa0(record);
  uint32_t first=*(volatile uint32_t *)(record+636u),second=*(volatile uint32_t *)(record+644u);
  *(volatile uint32_t *)(record+636u)=first|(1u<<21u);
  *(volatile uint32_t *)(record+644u)=second|(1u<<21u);
 }else if(action==2u)(void)opencfw_em9305_phy_reject_32698c(record,42u,1u);
 else if(action==3u){
  uint32_t bits=*(volatile uint32_t *)(record+644u),state=*(volatile uint8_t *)(record+625u);
  *(volatile uint32_t *)(record+648u)=0u;*(volatile uint32_t *)(record+644u)=bits&~(1u<<21u);
  if(state!=0u)*(volatile uint8_t *)(record+625u)=0u;
  uint32_t reason=*(volatile uint8_t *)(uintptr_t)0x80281du;
  (void)opencfw_em9305_phy_response_3232dc(record,reason);
 }
 return 1u;
}
