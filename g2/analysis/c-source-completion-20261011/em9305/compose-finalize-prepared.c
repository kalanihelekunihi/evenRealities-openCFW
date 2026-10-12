/* Native312bb4..312bbe: duration piece with 300-unit guard. */
uint32_t opencfw_em9305_compose_duration_guard_312bb4(uint32_t phy,uint32_t mode,uint32_t size)
{return opencfw_em9305_radio_duration_piece_312b88(phy,mode,size)+300u;}
/* Native323bac..323c08: auxiliary pointer field. Return retains native R0
 * (PHY high bits); the serialized byte2 is computed in native R2. */
uint32_t opencfw_em9305_compose_pointer_encode_323bac(uintptr_t record,uint32_t duration,uint32_t channel,uintptr_t output)
{
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805c18u;
 uint32_t metric=*(volatile uint16_t *)configuration;
 uint32_t quotient,selector;
 if(duration<0x3bfc4u){uint32_t reciprocal=0x11111112u;
  __asm__ volatile("mpymu %0,%1,%2":"=r"(quotient):"r"(duration),"r"(reciprocal));
  quotient>>=1;selector=0u;
 }else{uint32_t reciprocal=0x69d0369eu;
  __asm__ volatile("mpymu %0,%1,%2":"=r"(quotient):"r"(duration),"r"(reciprocal));
  quotient=((duration<<1)+duration+quotient)>>10;selector=128u;
 }
 volatile uint8_t *o=(volatile uint8_t *)output;
 o[0]=(uint8_t)(((metric<51u?1u:0u)<<6)|channel|selector);
 uint32_t phy=*(volatile uint8_t *)(record+63u);o[1]=(uint8_t)quotient;
 uint32_t bits=(phy==2u?1u:(phy==3u?2u:0u))<<13;
 o[2]=(uint8_t)((quotient|bits)>>8);return bits;
}
/* Native32412c..324274: complete eight-way finalization switch. */
uint32_t opencfw_em9305_compose_finalize_32412c(uintptr_t record,uintptr_t cursor,uintptr_t header,uint32_t present,uint32_t type)
{
 if(type>=8u||type==5u)return (uint32_t)record;
 if(type<=1u){*(volatile uint32_t *)(record+828u)=(uint32_t)cursor;
  *(volatile uint8_t *)(record+827u)=(uint8_t)present;
  *(volatile uint32_t *)(record+2780u)=0u;return (uint32_t)(record+2780u);
 }
 if(type==7u){*(volatile uint32_t *)(record+692u)=0u;return (uint32_t)record;}
 if(type==4u)*(volatile uint32_t *)(record+692u)=0u;
 else *(volatile uint32_t *)(record+2780u)=0u;
 if(cursor==0u)return type==2u?(uint32_t)(record+2780u):(uint32_t)record;
 uint32_t mode,phy,length;
 if(type==3u||type==6u){
  mode=*(volatile uint8_t *)(record+2531u);
  phy=*(volatile uint8_t *)(record+2528u);
  if(mode==0u)mode=*(volatile uint8_t *)(record+2693u);
  length=*(volatile uint8_t *)(header+4u);
 }else{
  length=*(volatile uint8_t *)(header+4u);
  mode=*(volatile uint8_t *)(record+2530u);
  phy=*(volatile uint8_t *)(record+2528u);
 }
 uint32_t piece=opencfw_em9305_compose_duration_guard_312bb4(phy,mode,length+2u);
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t record_guard=*(volatile uint32_t *)(record+72u);
 uint32_t config_guard=*(volatile uint16_t *)(configuration+20u);
 uint32_t duration=(record_guard>config_guard?record_guard:config_guard)+piece;
 uint32_t bounded=duration<0x257ed4u?duration:0x257ed4u;
 uint32_t channel;
 if(type==4u){channel=*(volatile uint8_t *)(record+697u);
  *(volatile uint32_t *)(record+692u)=bounded;
 }else{
  bounded=opencfw_em9305_channel_timing_adjust_312c5c(bounded);
  *(volatile uint32_t *)(record+2780u)=bounded;
  channel=*(volatile uint8_t *)(record+2784u);
  *(volatile uint32_t *)(record+2780u)=bounded;
 }
 return opencfw_em9305_compose_pointer_encode_323bac(record,bounded,channel,cursor);
}
