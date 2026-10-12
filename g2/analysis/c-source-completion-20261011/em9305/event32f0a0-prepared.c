/* Native event32f0a0..32f34c: full product-gated packet projection. */
uint32_t opencfw_em9305_dispatch_32f0a0(uintptr_t packet)
{
 uint32_t type=*(volatile uint8_t *)(packet+2u);
 uintptr_t base=0x8056e8u;
 uint32_t gate,mask,event_type=62u,size,subtype=0u,le=0u;
 switch(type){
 case 5u:gate=16u;mask=1u;size=19u;subtype=1u;le=1u;break;
 case 6u:gate=0u;mask=16u;size=4u;event_type=5u;break;
 case 7u:gate=16u;mask=4u;size=10u;subtype=3u;le=1u;break;
 case 9u:gate=1u;mask=8u;size=8u;event_type=12u;break;
 case 10u:gate=16u;mask=8u;size=12u;subtype=4u;le=1u;break;
 case 16u:gate=16u;mask=32u;size=11u;subtype=6u;le=1u;break;
 case 18u:gate=16u;mask=64u;size=11u;subtype=7u;break;
 case 46u:gate=19u;mask=64u;size=5u;subtype=31u;le=1u;break;
 case 47u:gate=20u;mask=1u;size=9u;subtype=33u;le=1u;break;
 case 48u:gate=19u;mask=128u;size=5u;subtype=32u;le=1u;break;
 default:return 0u;
 }
 if((*(volatile uint8_t *)(base+gate)&mask)==0u)return 0u;
 if(le!=0u&&(*(volatile uint8_t *)(base+7u)&32u)==0u)return 0u;
 uintptr_t event=opencfw_em9305_ll_event_allocate(event_type,size);
 if(event==0u)return 0u;
 if(subtype!=0u)*(volatile uint8_t *)event=(uint8_t)subtype;
 switch(type){
 case 5u:{
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<3u;++i)*(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
  uint32_t kind=*(volatile uint8_t *)(packet+9u);
  uintptr_t address;
  if((kind&~1u)==2u){*(volatile uint8_t *)(event+5u)=1u;address=packet+29u;}
  else{*(volatile uint8_t *)(event+5u)=(uint8_t)kind;address=packet+10u;}
  (void)opencfw_em9305_radio_address_copy_304604(event+6u,address);
  for(uint32_t i=0u;i<7u;++i)*(volatile uint8_t *)(event+12u+i)=*(volatile uint8_t *)(packet+16u+i);
  break;
 }
 case 6u:
  *(volatile uint8_t *)event=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<3u;++i)*(volatile uint8_t *)(event+1u+i)=*(volatile uint8_t *)(packet+6u+i);
  break;
 case 7u:
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<8u;++i)*(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
  break;
 case 9u:
  *(volatile uint8_t *)event=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<3u;++i)*(volatile uint8_t *)(event+1u+i)=*(volatile uint8_t *)(packet+6u+i);
  for(uint32_t i=0u;i<4u;++i)*(volatile uint8_t *)(event+4u+i)=*(volatile uint8_t *)(packet+10u+i);
  break;
 case 10u:
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<2u;++i)*(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
  (void)opencfw_em9305_memcpy((void *)(event+4u),(const void *)(packet+8u),8u);
  break;
 case 16u:case 18u:
  for(uint32_t i=0u;i<10u;++i)*(volatile uint8_t *)(event+1u+i)=*(volatile uint8_t *)(packet+4u+i);
  break;
 case 46u:
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<3u;++i)*(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
  break;
 case 47u:
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<7u;++i)*(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
  break;
 case 48u:
  for(uint32_t i=0u;i<4u;++i)*(volatile uint8_t *)(event+1u+i)=*(volatile uint8_t *)(packet+4u+i);
  break;
 }
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}
