/* Authenticated dispatch330ce0: native extended-report rejection returns1;
 * legacy rejection returns0. Allocation length wraps through low byte. */
uint32_t opencfw_em9305_dispatch_330ce0(uintptr_t input)
{
 uint32_t type=*(volatile uint8_t *)(input+2u);
 uintptr_t event;
 if(type==4u){
  event=opencfw_em9305_ll_event_allocate(14u,4u);
  if(event==0u)return 0u;
  *(volatile uint8_t *)(event+1u)=12u;
  *(volatile uint8_t *)event=1u;
  *(volatile uint8_t *)(event+2u)=32u;
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(input+3u);
 }else if(type==2u){
  uint32_t kind=*(volatile uint8_t *)(input+18u);
  uint32_t mask=*(volatile uint32_t *)(uintptr_t)0x8056f8u;
  uint32_t extended=kind!=255u;
  uint32_t rejected=extended;
  if((mask&(extended?1024u:2u))==0u)return rejected;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return rejected;
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805718u;
  if(count>=*(volatile uint8_t *)(config+14u))return rejected;
  uint32_t length=18u;
  if(!extended)length=(uint8_t)(*(volatile uint8_t *)(input+8u)+12u);
  event=opencfw_em9305_ll_event_allocate(62u,length);
  if(event==0u)return rejected;
  *(volatile uint8_t *)(event+1u)=1u;
  *(volatile uint8_t *)event=(uint8_t)(extended?11u:2u);
  *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(input+10u);
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(input+11u);
  (void)opencfw_em9305_radio_address_copy_304604(event+4u,input+12u);
  if(extended){
   *(volatile uint8_t *)(event+10u)=*(volatile uint8_t *)(input+18u);
   (void)opencfw_em9305_radio_address_copy_304604(event+11u,input+19u);
   *(volatile uint8_t *)(event+17u)=*(volatile uint8_t *)(input+9u);
  }else{
   *(volatile uint8_t *)(event+10u)=*(volatile uint8_t *)(input+8u);
   uint32_t bytes=*(volatile uint8_t *)(input+8u);
   uintptr_t data=*(volatile uint32_t *)(input+4u);
   (void)opencfw_em9305_memcpy((void *)(event+11u),(const void *)data,bytes);
   uint32_t fresh_bytes=*(volatile uint8_t *)(input+8u);
   uint32_t tail=*(volatile uint8_t *)(input+9u);
   *(volatile uint8_t *)(event+fresh_bytes+11u)=(uint8_t)tail;
  }
  count=*(volatile uint8_t *)(uintptr_t)0x805718u;
  *(volatile uint8_t *)(uintptr_t)0x805718u=(uint8_t)(count+1u);
 }else return 0u;
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}
