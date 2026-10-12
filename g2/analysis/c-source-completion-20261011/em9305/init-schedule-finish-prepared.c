extern uint32_t opencfw_em9305_init_schedule_adjust_312f88(uintptr_t,uint32_t,uint32_t);
/* Native325720..32573c. Native bit-test index is modulo32; masks with
 * no reachable bit can loop forever and no invented escape is introduced. */
uint32_t opencfw_em9305_init_channel_next_325720(uint32_t channel,uint32_t mask)
{
 if(mask==0u)return 37u;
 for(;;){channel+=1u;if((uint8_t)channel>39u)channel=37u;if(((mask>>((channel-37u)&31u))&1u)!=0u)return (uint8_t)channel;}
}
/* Complete native31ec40..31ed30, retains three-argument genuine adjust
 * contract, fresh loads and incidental native R0 on each return path. */
uint32_t opencfw_em9305_init_schedule_finish_31ec40(uintptr_t object)
{
 uintptr_t record=*(volatile uint32_t *)(object+36u),extra=record+240u;
 uint32_t pending=*(volatile uint8_t *)(record+149u);
 if(pending==0u)pending=*(volatile uint8_t *)(extra-92u);
 if(pending!=0u){
  uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
  if(message==0u)return 0u;
  *(volatile uint8_t *)(message+3u)=3u;
  uint32_t event=record!=0x804fd8u?3u:2u;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint8_t *)(message+2u)=(uint8_t)event;
  return opencfw_em9305_wsf_task_message_send(handler,message);
 }
 uint32_t update=*(volatile uint8_t *)(uintptr_t)0x805a80u;
 if(update!=0u){
  uint32_t flags=*(volatile uint8_t *)(record+65u);
  if((flags&1u)!=0u){
   *(volatile uint8_t *)(uintptr_t)0x805a80u=0u;
   if((flags&2u)==0u){uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805a90u;uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805a8cu;(void)opencfw_em9305_radio_address_write_3045e8(record+2u,low,high);}
   uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805a90u,low=*(volatile uint32_t *)(uintptr_t)0x805a8cu;
   *(volatile uint32_t *)(extra+48u)=high;*(volatile uint32_t *)(extra+44u)=low;
  }
 }
 uint32_t second=*(volatile uint16_t *)(record+62u),first=*(volatile uint16_t *)(record+60u);
 uint32_t time=*(volatile uint32_t *)(record+56u);
 *(volatile uint32_t *)(object+8u)=time;
 if(first!=second){
  uint32_t prior=*(volatile uint32_t *)(extra+124u),duration=*(volatile uint32_t *)(object+12u);
  uint32_t period=(uint32_t)(uint16_t)second*625u;
  if(duration+prior<period&&opencfw_em9305_init_schedule_adjust_312f88(object,prior,period)!=0u){
   time=*(volatile uint32_t *)(record+56u);
   uint32_t current=*(volatile uint32_t *)(object+8u);
   uint32_t result=opencfw_em9305_auxiliary_elapsed_303f8c(current,time);
   *(volatile uint32_t *)(extra+124u)=result;return result;
  }
 }
 uint32_t mask=*(volatile uint8_t *)(record+351u),channel=*(volatile uint8_t *)(record+201u);
 *(volatile uint32_t *)(extra+124u)=0u;
 channel=opencfw_em9305_init_channel_next_325720(channel,mask);
 second=*(volatile uint16_t *)(record+62u);first=*(volatile uint16_t *)(record+60u);
 *(volatile uint8_t *)(record+201u)=(uint8_t)channel;
 if(first==second){(void)opencfw_em9305_auxiliary_insert_313220(object);time=*(volatile uint32_t *)(object+8u);*(volatile uint32_t *)(record+56u)=time;return time;}
 first=(uint32_t)(uint16_t)first*625u;second=(uint32_t)(uint16_t)second*625u;
 time=*(volatile uint32_t *)(object+8u);uint32_t maximum=first+second;
 time+=first;*(volatile uint32_t *)(record+56u)=time;
 for(;;){
  uint32_t success=opencfw_em9305_init_schedule_adjust_312f88(object,first,maximum);
  time=*(volatile uint32_t *)(record+56u);
  if(success!=0u){uint32_t current=*(volatile uint32_t *)(object+8u);uint32_t result=opencfw_em9305_auxiliary_elapsed_303f8c(current,time);*(volatile uint32_t *)(extra+124u)=result;return result;}
  *(volatile uint32_t *)(object+8u)=time;time+=first;*(volatile uint32_t *)(record+56u)=time;
 }
}
