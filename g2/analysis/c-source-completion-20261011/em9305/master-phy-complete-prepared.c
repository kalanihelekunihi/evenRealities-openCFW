extern uintptr_t opencfw_em9305_phy_record_325250(uintptr_t);
extern uint32_t opencfw_em9305_phy_length_notify_32317c(uintptr_t,uint32_t);
/* Native315c64..315d3e full post-PHY data-length adjustment. */
uint32_t opencfw_em9305_phy_action_315c64(uintptr_t input)
{
 uintptr_t record=input;
 (void)opencfw_em9305_phy_record_325250(input);
 uint32_t bits=*(volatile uint32_t *)(record+636u);
 if((bits&(1u<<21u))==0u)return bits;
 *(volatile uint32_t *)(record+636u)=bits&~(1u<<21u);
 *(volatile uint32_t *)(record+640u)=0u;
 (void)opencfw_em9305_phy_response_3232dc(record,0u);
 uint32_t mode_first=*(volatile uint8_t *)(record+76u);
 uint32_t old_first=*(volatile uint16_t *)(record+580u);
 uint32_t octets_first=*(volatile uint16_t *)(record+578u),time_first=0u;
 if(mode_first-1u<2u){
  time_first=*(volatile uint16_t *)(record+588u);
  if(time_first!=0u)*(volatile uint16_t *)(record+588u)=0u;
  else{uint32_t limit=octets_first*8u+112u;time_first=limit<old_first?limit:old_first;}
 }else if(mode_first==3u){uint32_t limit=octets_first*64u+976u;time_first=limit<old_first?limit:old_first;}
 uint32_t mode_second=*(volatile uint8_t *)(record+77u);
 uint32_t old_second=*(volatile uint16_t *)(record+576u);
 uint32_t octets_second=*(volatile uint16_t *)(record+574u),time_second=328u;
 if(mode_second-1u<2u){
  uint32_t value=*(volatile uint16_t *)(record+584u);
  if(value!=0u)*(volatile uint16_t *)(record+584u)=0u;
  else{uint32_t limit=octets_second*8u+112u;value=limit<old_second?limit:old_second;}
  if(value>=329u)time_second=value;
 }else if(mode_second==3u){
  uint32_t limit=octets_second*64u+976u,value=limit<old_second?limit:old_second;
  *(volatile uint16_t *)(record+584u)=(uint16_t)old_second;
  time_second=value>2704u?value:2704u;
 }
 *(volatile uint16_t *)(record+576u)=(uint16_t)time_second;
 if(mode_first==3u){*(volatile uint16_t *)(record+588u)=(uint16_t)old_first;if(time_first<2704u)time_first=2704u;}
 else if(time_first<328u)time_first=328u;
 uint32_t feature=*(volatile uint8_t *)(uintptr_t)0x805a94u;
 *(volatile uint16_t *)(record+580u)=(uint16_t)time_first;
 if((feature&32u)!=0u&&(old_first!=time_first||old_second!=time_second))
  return opencfw_em9305_phy_length_notify_32317c(record,0u);
 return feature;
}
