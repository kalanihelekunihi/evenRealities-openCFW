/* Native32e470..32e48c: fixed249-byte allocation with variable payload header. */
uintptr_t opencfw_em9305_event_allocate_large_32e470(uint32_t type,uint32_t bytes)
{
 uintptr_t event=opencfw_em9305_wsf_event_allocate(249u);
 if(!event)return 0u;
 *(volatile uint8_t *)(event+1u)=(uint8_t)bytes;
 *(volatile uint8_t *)event=(uint8_t)type;
 return event+2u;
}
static inline uint32_t opencfw_em9305_event_mpyw_negative(uint32_t quotient,uint32_t divisor)
{
 uint32_t product;
 if(divisor==229u)__asm__ volatile("mpyw %0,%1,-229":"=r"(product):"r"(quotient));
 else __asm__ volatile("mpyw %0,%1,-247":"=r"(product):"r"(quotient));
 return product;
}
/* Native330848..330bdc: full event switch, live capacity and fragmented payloads. */
uint32_t opencfw_em9305_dispatch_330848(uintptr_t packet)
{
 uint32_t type=*(volatile uint8_t *)(packet+2u);
 uintptr_t event;
 if(type==23u||type==32u){
  uint32_t bit=type==23u?4u:6u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056f9u&(1u<<bit))==0u)return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return 0u;
  uint32_t divisor=type==23u?229u:247u;
  uint32_t length=*(volatile uint16_t *)(packet+(type==23u?28u:10u));
  uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t quotient=length/divisor;
  uint32_t negative=opencfw_em9305_event_mpyw_negative(quotient,divisor);
  uint32_t needed=(uint8_t)(quotient+((uint16_t)negative!=(uint16_t)(0u-length)));
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805718u;
  uint32_t capacity=*(volatile uint8_t *)(product+14u);
  if(needed+count>capacity)return 0u;
  uintptr_t data=*(volatile uint32_t *)(packet+(type==23u?32u:12u));
  uint32_t remaining=length,stopped;
  do{
   product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   count=*(volatile uint8_t *)(uintptr_t)0x805718u;
   uint32_t chunk=remaining<divisor?remaining:divisor;
   capacity=*(volatile uint8_t *)(product+14u);
   if(count>=capacity)return 0u;
   event=type==23u?opencfw_em9305_wsf_event_allocate(231u):opencfw_em9305_event_allocate_large_32e470(62u,(uint8_t)(chunk+8u));
   if(!event)return 0u;
   if(type==23u){*(volatile uint8_t *)event=62u;*(volatile uint8_t *)(event+1u)=(uint8_t)(chunk+26u);}
   product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   count=*(volatile uint8_t *)(uintptr_t)0x805718u;
   remaining-=chunk;
   capacity=*(volatile uint8_t *)(product+14u);
   uint32_t next=count+1u;
   if(type==23u){
    *(volatile uint8_t *)(uintptr_t)0x805718u=(uint8_t)next;
    stopped=(remaining!=0u)&&((uint8_t)next==capacity);
    uint32_t flags=*(volatile uint16_t *)(packet+4u);
    if(stopped){flags|=64u;remaining=0u;*(volatile uint16_t *)(packet+4u)=(uint16_t)flags;}
    uintptr_t initial=*(volatile uint32_t *)(packet+32u);
    uint32_t total=*(volatile uint16_t *)(packet+28u);
    uintptr_t end=data+chunk;
    uint32_t projected=(flags&31u)|32u;
    if(total==(uint16_t)(end-initial))projected=flags;
    *(volatile uint8_t *)(event+4u)=(uint8_t)projected;
    *(volatile uint8_t *)(event+3u)=1u;*(volatile uint8_t *)(event+2u)=13u;
    *(volatile uint8_t *)(event+5u)=(uint8_t)(projected>>8u);
    *(volatile uint8_t *)(event+6u)=*(volatile uint8_t *)(packet+6u);
    (void)opencfw_em9305_radio_address_copy_304604(event+7u,packet+7u);
    for(uint32_t i=13u;i<=20u;++i)*(volatile uint8_t *)(event+i)=*(volatile uint8_t *)(packet+i);
    (void)opencfw_em9305_radio_address_copy_304604(event+21u,packet+21u);
    *(volatile uint8_t *)(event+27u)=(uint8_t)chunk;
    (void)opencfw_em9305_memcpy((void *)(event+28u),(const void *)data,chunk);
    (void)opencfw_em9305_ll_event_send(event);data=end;
   }else{
    stopped=(remaining!=0u)&&((uint8_t)next==capacity);
    *(volatile uint8_t *)(uintptr_t)0x805718u=(uint8_t)next;
    if(stopped){remaining=0u;*(volatile uint8_t *)(packet+9u)=2u;}
    uintptr_t initial=*(volatile uint32_t *)(packet+12u);
    uint32_t total=*(volatile uint16_t *)(packet+10u);
    uintptr_t end=data+chunk;uint32_t projected=1u;
    if(total==(uint16_t)(end-initial))projected=(*(volatile uint8_t *)(packet+9u)==2u)?2u:0u;
    *(volatile uint8_t *)event=15u;
    for(uint32_t i=1u;i<=4u;++i)*(volatile uint8_t *)(event+i)=*(volatile uint8_t *)(packet+i+3u);
    uint32_t last=*(volatile uint8_t *)(packet+8u);
    *(volatile uint8_t *)(event+7u)=(uint8_t)chunk;
    *(volatile uint8_t *)(event+6u)=(uint8_t)projected;
    *(volatile uint8_t *)(event+5u)=(uint8_t)last;
    if((uint8_t)chunk)(void)opencfw_em9305_memcpy((void *)(event+8u),(const void *)data,chunk);
    (void)opencfw_em9305_ll_event_send(event-2u);data=end;
   }
  }while(remaining!=0u);
  return stopped^1u;
 }
 if(type==24u){
  event=opencfw_em9305_ll_event_allocate(14u,4u);if(!event)return 0u;
  *(volatile uint8_t *)(event+2u)=32u;*(volatile uint8_t *)(event+1u)=66u;
  *(volatile uint8_t *)event=1u;
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(packet+3u);
  (void)opencfw_em9305_ll_event_send(event-2u);return 1u;
 }
 if(type==25u){
  if((*(volatile uint8_t *)(uintptr_t)0x8056fau&1u)==0u)return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return 0u;
  event=opencfw_em9305_ll_event_allocate(62u,1u);if(!event)return 0u;
  *(volatile uint8_t *)event=17u;(void)opencfw_em9305_ll_event_send(event-2u);return 1u;
 }
 if(type==30u||type==31u||type==38u){
  uintptr_t feature=type==38u?0x8056fau:0x8056f9u;
  uint32_t bit=type==30u?5u:7u;
  if((*(volatile uint8_t *)feature&(1u<<bit))==0u)return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return 0u;
  uint32_t bytes=type==30u?16u:(type==31u?3u:20u);
  event=opencfw_em9305_ll_event_allocate(62u,bytes);if(!event)return 0u;
  if(type==31u){
   *(volatile uint8_t *)event=16u;
   *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
   *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(packet+5u);
  }else{
   *(volatile uint8_t *)event=type==30u?14u:24u;
   *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
   uint32_t last=type==30u?5u:9u;
   for(uint32_t i=2u;i<=last;++i)*(volatile uint8_t *)(event+i)=*(volatile uint8_t *)(packet+i+4u);
   uint32_t dest=type==30u?6u:10u,src=type==30u?10u:14u;
   (void)opencfw_em9305_radio_address_copy_304604(event+dest,packet+src);
   *(volatile uint8_t *)(event+dest+6u)=*(volatile uint8_t *)(packet+src+6u);
   for(uint32_t i=7u;i<=9u;++i)*(volatile uint8_t *)(event+dest+i)=*(volatile uint8_t *)(packet+src+i+1u);
  }
  (void)opencfw_em9305_ll_event_send(event-2u);return 1u;
 }
 return 0u;
}
