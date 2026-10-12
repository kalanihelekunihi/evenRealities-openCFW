/* Native327544..32754a full first-PHY state setter. */
uint32_t opencfw_em9305_phy_apply_327544(uintptr_t record,uint32_t value)
{ *(volatile uint8_t *)(record+597u)=(uint8_t)value;return (uint32_t)(record+597u); }
/* Native316610..316696 full PHY preference selector, including incidental R0. */
uint32_t opencfw_em9305_phy_choose_316610(uintptr_t record,uint32_t flags,uintptr_t first,uintptr_t second,uint32_t preferred)
{
 uint32_t b=*(volatile uint8_t *)second,a;
 if((flags&1u)==0u)a=*(volatile uint8_t *)first;
 else a=opencfw_em9305_phy_supported_31b39c();
 if((flags&2u)!=0u)b=opencfw_em9305_phy_supported_31b39c();
 uint32_t result=*(volatile uint8_t *)(record+4u);
 if((result&128u)!=0u){
  b&=a;
  if((uint8_t)b!=0u){
   uint32_t chosen=b&preferred;
   if(chosen!=0u)b=chosen;
   result=opencfw_em9305_radio_phy_project_3183d4((uint8_t)b);
   a=result;b=result;
  }else{
   uint32_t mode_first=*(volatile uint8_t *)(record+76u);
   uint32_t mode_second=*(volatile uint8_t *)(record+77u);
   uint32_t index=mode_first-2u;
   result=(uint8_t)index*8u;
   a=index>=3u?1u:(0x00080402u>>(index*8u));
   b=mode_second==4u?8u:mode_second==3u?4u:mode_second==2u?2u:1u;
  }
 }
 *(volatile uint8_t *)first=(uint8_t)a;
 *(volatile uint8_t *)second=(uint8_t)b;
 return result;
}
/* Native32e220..32e276 full pending update queue drain. */
uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t record)
{
 *(volatile uint8_t *)(record+404u)=0u;
 uintptr_t queue=record+352u;
 uint32_t empty=opencfw_em9305_wsf_queue_empty(queue);
 if(empty!=0u)return empty;
 uint32_t capacity=opencfw_em9305_ll_event_mode_32d4b0(record);
 _Alignas(4) uint8_t decoded[8];uint8_t handler;
 for(;;){
  uintptr_t message=opencfw_em9305_wsf_event_remove(queue,(uintptr_t)&handler);
  if(message==0u)break;
  (void)opencfw_em9305_ll_event_decode_32dae4((uintptr_t)decoded,message);
  (void)opencfw_em9305_ll_event_process_32d380(record,capacity,(uintptr_t)decoded,message);
 }
 uint32_t event_handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 return opencfw_em9305_wsf_event_post(event_handler,4u);
}
