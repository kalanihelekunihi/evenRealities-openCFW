/* Native3136ac..3136fa: exclude removed ID, recalculate strict maximum,
 * then retain callback-fresh counter and full decrement return. */
uint32_t opencfw_em9305_associated_schedule_drop_3136ac(uint32_t id)
{
 uintptr_t root=0x805f28u;
 uint32_t existing=*(volatile uint32_t *)(root+8u);
 uint32_t selected=*(volatile uint32_t *)(root+(id&65535u)*12u+52u);
 if(selected==existing){
  uint32_t maximum=0u;
  for(uint32_t index=0u;index<8u;++index){
   if(index==id)continue;
   uint32_t candidate=*(volatile uint32_t *)(root+16u+index*4u);
   if(candidate!=0u&&candidate>maximum)maximum=candidate;
  }
  (void)opencfw_em9305_radio_primary_timer_333bec(maximum);
 }
 uint32_t count=*(volatile uint8_t *)root;
 *(volatile uint32_t *)(root+id*4u)=0u;
 count-=1u;*(volatile uint8_t *)root=(uint8_t)count;
 return count;
}
/* Native3266d0..3266f6: cleanup event4B actual byte order and R0 send return. */
uint32_t opencfw_em9305_associated_cleanup_3266d0(uintptr_t record,uint32_t action)
{
 uintptr_t event=opencfw_em9305_wsf_event_allocate(4u);
 if(event==0u)return 0u;
 uint32_t id=*(volatile uint8_t *)(record+1u),handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(event+3u)=(uint8_t)action;
 *(volatile uint16_t *)event=(uint16_t)id;
 *(volatile uint8_t *)(event+2u)=10u;
 return opencfw_em9305_wsf_task_message_send(handler,event);
}
