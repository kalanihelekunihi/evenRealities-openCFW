/* Native32e918..32eb30: complete response router. Allocation captures the
 * command before call, then routing reloads the request after allocation.
 * Unwritten packet bytes and provider-owned scratch stay native sparse. */
extern uint32_t opencfw_em9305_primary_query_30bf04(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_query_30c92c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_query_30bb74(uintptr_t);
extern uint32_t opencfw_em9305_primary_query_30bdb4(uintptr_t);
extern uint32_t opencfw_em9305_primary_query_30bf20(uint32_t);
extern uint32_t opencfw_em9305_primary_query_30bea4(uintptr_t);
extern uint32_t opencfw_em9305_primary_query_30c928(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_query_313960(uintptr_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_primary_response_32e918(uintptr_t request,uint32_t status,uint32_t length)
{
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(packet==0u)return 0u;
 uint32_t command=*(volatile uint16_t *)request;
 _Alignas(4) uint8_t scratch[24];
 switch(command){
 case 0x2002u:{
  uint32_t first=opencfw_em9305_ll_test_30bb14();
  uint32_t second=opencfw_em9305_ll_test_30bb20();
  *(volatile uint8_t *)(packet+3u)=(uint8_t)second;
  *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
  *(volatile uint8_t *)packet=(uint8_t)status;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)(first>>8u);break;
 }
 case 0x1001u:{
  (void)opencfw_em9305_primary_query_30bf04((uintptr_t)scratch,(uintptr_t)(scratch+23u),(uintptr_t)(scratch+20u));
  *(volatile uint8_t *)packet=(uint8_t)status;
  uint32_t single=*(volatile uint8_t *)(scratch+23u);
  *(volatile uint8_t *)(packet+1u)=(uint8_t)single;
  uint32_t word=*(volatile uint16_t *)(scratch+20u);
  *(volatile uint8_t *)(packet+4u)=(uint8_t)single;
  uint32_t first=*(volatile uint16_t *)scratch;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)word;
  *(volatile uint8_t *)(packet+7u)=(uint8_t)word;
  *(volatile uint8_t *)(packet+5u)=(uint8_t)first;
  *(volatile uint8_t *)(packet+3u)=(uint8_t)(word>>8u);
  *(volatile uint8_t *)(packet+8u)=(uint8_t)(word>>8u);
  *(volatile uint8_t *)(packet+6u)=(uint8_t)(first>>8u);break;
 }
 case 0x204bu:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_primary_query_30c92c(packet+1u,packet+2u);break;
 case 0x1009u:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_primary_query_30bb74(packet+1u);break;
 case 0x2003u:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_primary_query_30bdb4(packet+1u);break;
 case 0x200fu:{
  *(volatile uint8_t *)packet=(uint8_t)status;
  uint32_t result=opencfw_em9305_primary_query_30bf20(command);
  *(volatile uint8_t *)(packet+1u)=(uint8_t)result;break;
 }
 case 0x2018u:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_radio_random_bytes_310038(packet+1u,8u);break;
 case 0x201cu:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_primary_query_30bea4(packet+1u);break;
 case 0x201fu:{
  (void)opencfw_em9305_memset(scratch,0u,20u);
  uint32_t result=opencfw_em9305_command_stop_30b654((uintptr_t)scratch);
  *(volatile uint8_t *)packet=(uint8_t)result;
  uint32_t first=*(volatile uint8_t *)(scratch+2u);
  *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
  uint32_t second=*(volatile uint8_t *)(scratch+3u);
  *(volatile uint8_t *)(packet+2u)=(uint8_t)second;break;
 }
 case 0x204cu:{
  (void)opencfw_em9305_primary_query_30c928((uintptr_t)scratch,(uintptr_t)(scratch+20u));
  *(volatile uint8_t *)packet=(uint8_t)status;
  uint32_t first=*(volatile uint8_t *)scratch;
  *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
  uint32_t value=*(volatile uint16_t *)(scratch+20u);
  uint32_t second=*(volatile uint8_t *)(scratch+1u);
  *(volatile uint8_t *)(packet+3u)=(uint8_t)value;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)second;
  *(volatile uint8_t *)(packet+4u)=(uint8_t)(value>>8u);break;
 }
 case 0x0c48u:
  *(volatile uint8_t *)packet=(uint8_t)status;
  *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)(uintptr_t)0x80571au;break;
 case 0x1002u:
  (void)opencfw_em9305_memset((void *)(packet+1u),0u,64u);
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_memcpy((void *)(packet+1u),(void *)(uintptr_t)0x805885u,64u);break;
 case 0x1003u:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_primary_query_313960(packet+1u,0u,96u);break;
 case 0u:case 0x0c01u:case 0x0c49u:case 0x0c63u:case 0x0c82u:case 0x0c84u:
 case 0x2001u:case 0x2005u:case 0x2010u:case 0x2011u:case 0x2012u:case 0x201du:case 0x201eu:
 case 0x204du:case 0x204fu:case 0x2050u:case 0x205fu:case 0x2074u:case 0x207bu:
  *(volatile uint8_t *)packet=(uint8_t)status;break;
 default:break;
 }
 return opencfw_em9305_ll_event_send(packet-5u);
}
