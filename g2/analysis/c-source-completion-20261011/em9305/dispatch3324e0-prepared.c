extern uint32_t opencfw_em9305_dispatch_3328c8(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_field_30cee0(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_extended_packet_30d678(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_packet_30d5ac(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_data_30d580(uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_response_30d854(uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_enable_rows_30b6cc(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_clear_30ca00(uint32_t);
extern uint32_t opencfw_em9305_command_clear_all_30b118(void);
extern uint32_t opencfw_em9305_command_intervals_30db34(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_periodic_data_30dac8(uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_periodic_enable_30daf8(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_packet_power_30bd8c(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_packet_count_30c7b0(uintptr_t);
extern uint32_t opencfw_em9305_command_packet_size_30c768(uintptr_t);
/* Native3324e0..3327f4: complete packet/periodic command projection,
 * sparse scratch records, fresh response opcode and status paths. */
uint32_t opencfw_em9305_dispatch_3324e0(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_dispatch_3328c8(request,input)!=0u)return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 if(command-0x2035u>=12u&&command!=0x207fu)return 0u;
 uint8_t scratch[32] __attribute__((aligned(4)));uint32_t status=0u,id=255u,size=1u;
 switch(command){
 case 0x2035u:id=*(volatile uint8_t *)input;status=opencfw_em9305_command_field_30cee0(id,input+1u);break;
 case 0x2036u:case 0x207fu:{
  if(command==0x2036u)(void)opencfw_em9305_memset(scratch,0u,32u);
  id=*(volatile uint8_t *)input;
  uint32_t first=*(volatile uint8_t *)(input+1u)+((uint32_t)*(volatile uint8_t *)(input+2u)<<8);
  uint32_t lower=*(volatile uint8_t *)(input+3u)+((uint32_t)*(volatile uint8_t *)(input+4u)<<8)+((uint32_t)*(volatile uint8_t *)(input+5u)<<16);
  uint32_t upper=*(volatile uint8_t *)(input+6u)+((uint32_t)*(volatile uint8_t *)(input+7u)<<8)+((uint32_t)*(volatile uint8_t *)(input+8u)<<16);
  uint32_t a=*(volatile uint8_t *)(input+9u),b=*(volatile uint8_t *)(input+10u),c=*(volatile uint8_t *)(input+11u);
  uint32_t extra=command==0x207fu?9u:7u;uint8_t tail[9];for(uint32_t j=0u;j<extra;++j)tail[j]=*(volatile uint8_t *)(input+18u+j);
  *(uint16_t *)(void *)scratch=(uint16_t)first;*(uint32_t *)(void *)(scratch+4u)=lower;*(uint32_t *)(void *)(scratch+8u)=upper;
  scratch[12]=(uint8_t)a;scratch[13]=(uint8_t)b;scratch[14]=(uint8_t)c;*(uint32_t *)(void *)(scratch+16u)=(uint32_t)(input+12u);
  for(uint32_t j=0u;j<extra;++j)scratch[20u+j]=tail[j];
  if(command==0x207fu){status=opencfw_em9305_command_extended_packet_30d678(id,(uintptr_t)scratch);*(volatile uint8_t *)(input+27u)=(uint8_t)status;}
  else{status=opencfw_em9305_command_packet_30d5ac(id,(uintptr_t)scratch);*(volatile uint8_t *)(input+25u)=(uint8_t)status;}
  size=2u;break;}
 case 0x2037u:case 0x2038u:{uint32_t d=*(volatile uint8_t *)(input+3u),c=*(volatile uint8_t *)(input+2u),b=*(volatile uint8_t *)(input+1u),a=*(volatile uint8_t *)input;
  status=command==0x2037u?opencfw_em9305_command_data_30d580(a,b,c,d,input+4u):opencfw_em9305_command_response_30d854(a,b,c,d,input+4u);break;}
 case 0x2039u:{uint32_t count=*(volatile uint8_t *)(input+1u),enable=*(volatile uint8_t *)input,n=count<2u?count:2u;uintptr_t cursor=input+2u;
  for(uint32_t j=0u;j<n;++j){uint32_t high=*(volatile uint8_t *)(cursor+2u),low=*(volatile uint8_t *)(cursor+1u),a=*(volatile uint8_t *)cursor,b=*(volatile uint8_t *)(cursor+3u);scratch[j*6u]=(uint8_t)a;scratch[j*6u+4u]=(uint8_t)b;*(uint16_t *)(void *)(scratch+j*6u+2u)=(uint16_t)(low+(high<<8));cursor+=4u;}
  (void)opencfw_em9305_command_enable_rows_30b6cc(enable,count,(uintptr_t)scratch);return 1u;}
 case 0x203au:size=3u;break;
 case 0x203bu:size=2u;break;
 case 0x203cu:status=opencfw_em9305_command_clear_30ca00(*(volatile uint8_t *)input);break;
 case 0x203du:status=opencfw_em9305_command_clear_all_30b118();break;
 case 0x203eu:{uint32_t a=*(volatile uint8_t *)(input+1u)+((uint32_t)*(volatile uint8_t *)(input+2u)<<8),b=*(volatile uint8_t *)(input+3u)+((uint32_t)*(volatile uint8_t *)(input+4u)<<8),c=*(volatile uint8_t *)(input+5u)+((uint32_t)*(volatile uint8_t *)(input+6u)<<8);id=*(volatile uint8_t *)input;*(uint16_t *)(void *)scratch=a;*(uint16_t *)(void *)(scratch+2u)=b;*(uint16_t *)(void *)(scratch+4u)=c;status=opencfw_em9305_command_intervals_30db34(id,(uintptr_t)scratch);break;}
 case 0x203fu:{uint32_t c=*(volatile uint8_t *)(input+2u),b=*(volatile uint8_t *)(input+1u),a=*(volatile uint8_t *)input;status=opencfw_em9305_command_periodic_data_30dac8(a,b,c,input+3u);break;}
 case 0x2040u:{uint32_t b=*(volatile uint8_t *)(input+1u),a=*(volatile uint8_t *)input;(void)opencfw_em9305_command_periodic_enable_30daf8(a,b);return 1u;}
 }
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(size,*(volatile uint16_t *)request);if(response==0u)return 1u;
 command=*(volatile uint16_t *)request;
 if(command==0x2036u||command==0x207fu){(void)opencfw_em9305_command_packet_power_30bd8c(id,(uintptr_t)scratch);*(volatile uint8_t *)response=(uint8_t)status;*(volatile uint8_t *)(response+1u)=scratch[0];}
 else if(command==0x203bu){scratch[0]=1u;uint32_t result=opencfw_em9305_command_packet_count_30c7b0((uintptr_t)scratch);*(volatile uint8_t *)response=(uint8_t)result;*(volatile uint8_t *)(response+1u)=scratch[0];}
 else if(command==0x203au){*(uint16_t *)(void *)scratch=31u;uint32_t result=opencfw_em9305_command_packet_size_30c768((uintptr_t)scratch);*(volatile uint8_t *)response=(uint8_t)result;*(volatile uint8_t *)(response+1u)=scratch[0];*(volatile uint8_t *)(response+2u)=scratch[1];}
 else if(command-0x2035u<12u||command==0x2080u)*(volatile uint8_t *)response=(uint8_t)status;
 (void)opencfw_em9305_ll_event_send(response-5u);return 1u;
}
