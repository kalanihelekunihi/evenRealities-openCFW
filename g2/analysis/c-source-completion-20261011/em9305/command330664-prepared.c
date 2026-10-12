/* Native330664..330848 full command parent. Deeper provider ABIs from call sites; bodies unresolved. */
extern uint32_t opencfw_em9305_command_prehandle_330bdc(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_scan_params_30b9f4(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_create_30c488(uintptr_t);
extern uint32_t opencfw_em9305_command_disable_30c54c(void);
extern uint32_t opencfw_em9305_command_timeout_30c600(uint32_t);
extern uint32_t opencfw_em9305_command_address_add_30aed4(uintptr_t);
extern uint32_t opencfw_em9305_command_address_remove_30ca1c(uintptr_t);
extern uint32_t opencfw_em9305_command_address_clear_30b12c(void);
extern uint32_t opencfw_em9305_command_scan_extended_30d774(uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_power_query_30c80c(uintptr_t);
uint32_t opencfw_em9305_dispatch_330664(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_command_prehandle_330bdc(request,input)!=0u)return 1u;
 uint32_t opcode=*(volatile uint16_t *)request,slot=opcode-0x2041u,status=0u;
 if(slot>9u)return 0u;
 _Alignas(4) uint8_t scratch[24];
 switch(slot){
 case 0u:{
  uint32_t first=*(volatile uint8_t *)input,second=*(volatile uint8_t *)(input+1u),mask=*(volatile uint8_t *)(input+2u);
  scratch[0]=(uint8_t)first;scratch[1]=(uint8_t)second;scratch[2]=(uint8_t)mask;
  uintptr_t cursor=input+3u;uint32_t count=0u;
  for(uint32_t bit=0u;bit<=7u&&count<=2u;++bit){
   if((mask&(1u<<bit))!=0u){
    uint32_t hi_a=*(volatile uint8_t *)(cursor+2u),hi_b=*(volatile uint8_t *)(cursor+4u);
    uint32_t lo_a=*(volatile uint8_t *)(cursor+1u),lo_b=*(volatile uint8_t *)(cursor+3u);
    uint32_t flags=*(volatile uint8_t *)cursor;
    uintptr_t row=(uintptr_t)scratch+count*6u;
    count++;cursor+=5u;
    *(uint8_t *)(row+8u)=(uint8_t)flags;
    *(uint16_t *)(row+4u)=(uint16_t)(lo_a+(hi_a<<8u));
    *(uint16_t *)(row+6u)=(uint16_t)(lo_b+(hi_b<<8u));
   }
  }
  status=opencfw_em9305_command_scan_extended_30d774(first,second,mask,(uintptr_t)scratch+4u);break;
 }
 case 1u:{
  uint32_t ah=*(volatile uint8_t *)(input+3u),bh=*(volatile uint8_t *)(input+5u);
  uint32_t al=*(volatile uint8_t *)(input+2u),bl=*(volatile uint8_t *)(input+4u);
  uint32_t second=*(volatile uint8_t *)(input+1u),first=*(volatile uint8_t *)input;
  (void)opencfw_em9305_command_scan_params_30b9f4(first,second,al+(ah<<8u),bl+(bh<<8u));return 1u;
 }
 case 2u:return 0u;
 case 3u:{
  uint32_t ah=*(volatile uint8_t *)(input+10u),bh=*(volatile uint8_t *)(input+12u),flags=*(volatile uint8_t *)input;
  uint32_t al=*(volatile uint8_t *)(input+9u),bl=*(volatile uint8_t *)(input+11u);
  uint32_t second=*(volatile uint8_t *)(input+1u),third=*(volatile uint8_t *)(input+2u),last=*(volatile uint8_t *)(input+13u);
  scratch[0]=(uint8_t)flags;scratch[1]=(uint8_t)second;scratch[2]=(uint8_t)third;
  *(uint32_t *)(scratch+4u)=(uint32_t)(input+3u);
  scratch[12]=(uint8_t)last;
  *(uint16_t *)(scratch+8u)=(uint16_t)(al+(ah<<8u));*(uint16_t *)(scratch+10u)=(uint16_t)(bl+(bh<<8u));
  if((flags&2u)!=0u&&(*(volatile uint8_t *)(uintptr_t)0x8058adu&32u)==0u)status=62u;
  else if((flags&4u)!=0u&&(*(volatile uint8_t *)(uintptr_t)0x805b34u&16u)==0u)status=17u;
  else status=opencfw_em9305_command_create_30c488((uintptr_t)scratch);
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);return 1u;
 }
 case 4u:status=opencfw_em9305_command_disable_30c54c();break;
 case 5u:{uint32_t high=*(volatile uint8_t *)(input+1u),low=*(volatile uint8_t *)input;status=opencfw_em9305_command_timeout_30c600(low+(high<<8u));break;}
 case 6u:case 7u:{
  uint32_t first=*(volatile uint8_t *)input,last=*(volatile uint8_t *)(input+7u);
  *(uint32_t *)(scratch+4u)=(uint32_t)(input+1u);scratch[0]=(uint8_t)first;scratch[8]=(uint8_t)last;
  status=slot==6u?opencfw_em9305_command_address_add_30aed4((uintptr_t)scratch):opencfw_em9305_command_address_remove_30ca1c((uintptr_t)scratch);break;
 }
 case 8u:status=opencfw_em9305_command_address_clear_30b12c();break;
 case 9u:break;
 }
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(slot==9u?2u:1u,*(volatile uint16_t *)request);
 if(response==0u)return 1u;
 uint32_t fresh=*(volatile uint16_t *)request,position=fresh-0x2041u;
 if((position<10u&&(499u&(1u<<position))!=0u)||fresh==0x2081u)*(volatile uint8_t *)response=(uint8_t)status;
 else if(position==9u){
  scratch[0]=0u;
  uint32_t result=opencfw_em9305_command_power_query_30c80c((uintptr_t)scratch);
  *(volatile uint8_t *)response=(uint8_t)result;
  *(volatile uint8_t *)(response+1u)=scratch[0];
 }
 (void)opencfw_em9305_ll_event_send(response-5u);return 1u;
}
