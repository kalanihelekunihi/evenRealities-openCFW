/* Authenticated dispatch3316e0..331814. Scratch padding untouched; fresh
 * request command after allocation governs response query/status layout. */
extern uint32_t opencfw_em9305_command_30d4e4(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30dd04(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30cba0(uintptr_t);
extern uint32_t opencfw_em9305_command_30e120(uintptr_t);
extern uint32_t opencfw_em9305_command_query_30c824(uint32_t,uintptr_t,uintptr_t);
uint32_t opencfw_em9305_dispatch_3316e0(uintptr_t request,uintptr_t input)
{
 uint32_t index=(uint32_t)*(volatile uint16_t *)request-0x2030u;
 if(index>=5u)return 0u;
 _Alignas(4) uint8_t scratch[24];
 uint32_t status=0u,id=0u,length=1u;
 if(index==0u){
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b0=*(volatile uint8_t *)input;
  id=b0+(b1<<8u);length=5u;
 }else if(index==1u){
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b0=*(volatile uint8_t *)input;
  status=opencfw_em9305_command_30d4e4(b0,b1,b2);
 }else if(index==2u){
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b6=*(volatile uint8_t *)(input+6u);
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b5=*(volatile uint8_t *)(input+5u);
  uint32_t b4=*(volatile uint8_t *)(input+4u);
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  status=opencfw_em9305_command_30dd04((uint16_t)(b0+(b1<<8u)),b2,b3,b4,(uint16_t)(b5+(b6<<8u)));
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);
  return 1u;
 }else if(index==3u){
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  *(volatile uint8_t *)(scratch+10u)=(uint8_t)b2;
  *(volatile uint16_t *)scratch=0u;
  *(volatile uint32_t *)(scratch+16u)=0u;
  *(volatile uint8_t *)(scratch+14u)=2u;
  *(volatile uint8_t *)(scratch+11u)=0u;
  *(volatile uint32_t *)(scratch+4u)=0x71764129u;
  *(volatile uint16_t *)(scratch+12u)=256u;
  *(volatile uint8_t *)(scratch+8u)=(uint8_t)b0;
  *(volatile uint8_t *)(scratch+9u)=(uint8_t)b1;
  status=opencfw_em9305_command_30cba0((uintptr_t)scratch);
 }else{
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  *(volatile uint8_t *)(scratch+5u)=(uint8_t)b3;
  *(volatile uint16_t *)scratch=0u;
  *(volatile uint32_t *)(scratch+12u)=0u;
  *(volatile uint8_t *)(scratch+8u)=2u;
  *(volatile uint16_t *)(scratch+6u)=0u;
  *(volatile uint8_t *)(scratch+16u)=127u;
  *(volatile uint8_t *)(scratch+2u)=(uint8_t)b0;
  *(volatile uint8_t *)(scratch+3u)=(uint8_t)b1;
  *(volatile uint8_t *)(scratch+4u)=(uint8_t)b2;
  status=opencfw_em9305_command_30e120((uintptr_t)scratch);
 }
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(response==0u)return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 if(command-0x2033u<2u||command==0x2031u)*(volatile uint8_t *)response=(uint8_t)status;
 else if(command==0x2030u){
  *(volatile uint8_t *)scratch=0u;
  *(volatile uint8_t *)(scratch+23u)=0u;
  uint32_t result=opencfw_em9305_command_query_30c824((uint16_t)id,(uintptr_t)scratch,(uintptr_t)(scratch+23u));
  uint32_t first=*(volatile uint8_t *)scratch;
  uint32_t second=*(volatile uint8_t *)(scratch+23u);
  *(volatile uint8_t *)(response+1u)=(uint8_t)id;
  *(volatile uint8_t *)response=(uint8_t)result;
  *(volatile uint8_t *)(response+2u)=(uint8_t)(id>>8u);
  *(volatile uint8_t *)(response+4u)=(uint8_t)second;
  *(volatile uint8_t *)(response+3u)=(uint8_t)first;
 }
 (void)opencfw_em9305_ll_event_send(response-5u);
 return 1u;
}
