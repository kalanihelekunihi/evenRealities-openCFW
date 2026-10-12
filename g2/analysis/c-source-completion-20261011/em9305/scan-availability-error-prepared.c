/* Native307b9c..307bdc: authenticated table3357b4 words8035dc/802a60/80389c. */
uint32_t opencfw_em9305_scan_available_307b9c(void)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805a81u!=0u)return 1u;
 static const uintptr_t states[3]={0x8035dcu,0x802a60u,0x80389cu};
 uint32_t mask=*(volatile uint8_t *)(uintptr_t)0x803560u;
 for(uint32_t bit=0u;bit<3u;++bit){
  if((mask&(1u<<bit))!=0u){
   uint32_t kind=*(volatile uint8_t *)(states[bit]+13u);
   if(opencfw_em9305_ll_stream_kind_valid_30e4dc(kind)==0u)return 0u;
   mask=*(volatile uint8_t *)(uintptr_t)0x803560u;
  }
 }
 return 1u;
}
/* Native30e7f8..30e834: first nonzero error latch, byte countdown, event24. */
uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t status)
{
 uintptr_t root=0x805a70u;
 uint32_t latched=*(volatile uint8_t *)(root+14u);
 if(status!=0u&&latched==0u){latched=status;*(volatile uint8_t *)(root+14u)=(uint8_t)status;}
 uint32_t count=*(volatile uint8_t *)(root+13u);
 if(count==0u)return 0u;
 uint32_t remaining=count-1u;
 *(volatile uint8_t *)(root+13u)=(uint8_t)remaining;
 if((uint8_t)remaining!=0u)return remaining;
 _Alignas(4) uint8_t event[5];
 *(volatile uint8_t *)(event+4u)=(uint8_t)latched;
 *(volatile uint8_t *)(event+3u)=(uint8_t)latched;
 *(volatile uint8_t *)(event+2u)=24u;
 *(volatile uint16_t *)(void *)event=0u;
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
