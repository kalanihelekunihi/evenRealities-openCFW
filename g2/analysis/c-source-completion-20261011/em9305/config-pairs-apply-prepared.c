/* Native306b80..306c44: clipped two-row link/channel mutation, latch and six-byte message. */
uint32_t opencfw_em9305_config_pairs_apply_306b80(uint32_t count,uintptr_t arrays)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805ab1u!=0u)return 12u;
 uint32_t limit=count<2u?count:2u;
 for(uint32_t i=0u;i<limit;++i){
  uintptr_t first=*(volatile uint32_t *)arrays;
  uint32_t id=*(volatile uint16_t *)(first+i*2u);
  uintptr_t link=opencfw_em9305_ll_link_find_31ab88(id);
  if(link==0u)return 2u;
  if(opencfw_em9305_ll_link_state_ready_31b750(link)!=0u)return 11u;
  uintptr_t channel=opencfw_em9305_ll_test_channel_find_31ab50(*(volatile uint8_t *)(link+11u));
  *(volatile uint8_t *)(channel+1u)=1u;
  *(volatile uint8_t *)(link+25u)=0u;
 }
 *(volatile uint8_t *)(uintptr_t)0x802a48u=(uint8_t)limit;
 *(volatile uint8_t *)(uintptr_t)0x805ab1u=1u;
 for(uint32_t i=0u;i<limit;++i){
  uintptr_t first=*(volatile uint32_t *)arrays,second=*(volatile uint32_t *)(arrays+4u);
  uint32_t a=*(volatile uint16_t *)(first+i*2u);
  *(volatile uint16_t *)(uintptr_t)(0x802a4au+i*2u)=(uint16_t)a;
  uint32_t b=*(volatile uint16_t *)(second+i*2u);
  *(volatile uint16_t *)(uintptr_t)(0x802a4eu+i*2u)=(uint16_t)b;
  *(volatile uint8_t *)(uintptr_t)(0x802a52u+i)=0u;
 }
 uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
 if(message==0u)return 0u;
 uint32_t second=*(volatile uint16_t *)(uintptr_t)0x802a4eu;
 *(volatile uint16_t *)(message+2u)=0x2401u;
 *(volatile uint16_t *)message=(uint16_t)second;
 uint32_t first=*(volatile uint16_t *)(uintptr_t)0x802a4au;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)(message+4u)=(uint16_t)first;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}
