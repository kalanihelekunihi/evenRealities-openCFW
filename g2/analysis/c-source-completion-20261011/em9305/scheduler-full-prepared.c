/* Authenticated native313424..31369a: complete scheduling offset selector.
 * Variable names track native saved registers where modular width matters.
 * Native DIVU destination prior, DIV signed and MACWHUL remain genuine ISA. */
static uint32_t opencfw_em9305_schedule_remu(uint32_t value,uint32_t divisor)
{uint32_t result;__asm__ volatile("remu %0,%1,%2":"=r"(result):"r"(value),"r"(divisor));return result;}
uint32_t opencfw_em9305_radio_schedule_313424(uint32_t incoming,uint32_t index,uint32_t timestamp,uint32_t existing,uint32_t action)
{
 uintptr_t original_head=*(volatile uint32_t *)(uintptr_t)0x805f14u;
 if(original_head==0u)return incoming;
 uintptr_t first=original_head;
 while(*(volatile uint32_t *)(first+20u)==0u){first=*(volatile uint32_t *)(first+4u);if(first==0u)return incoming;}
 uintptr_t selected=first;
 while(*(volatile uint8_t *)(selected+25u)==1u||*(volatile uint32_t *)(selected+20u)==0u){selected=*(volatile uint32_t *)(selected+4u);if(selected==0u)break;}
 uint32_t absent=selected==0u?1u:0u;
 uint32_t first_special=*(volatile uint8_t *)(first+25u)==1u?1u:0u;
 if(absent!=0u||first_special==0u)selected=first;
 uint64_t bitmap=opencfw_em9305_associated_bitmap_3336d8(selected,first_special&absent);
 uint32_t r13=0u,fp=0u;
 uintptr_t root=0x805f28u;
 if(action==3u){
  uintptr_t node=original_head;
  while(node!=(uintptr_t)existing){node=*(volatile uint32_t *)(node+4u);if(node==0u)goto compose_offset;}
  uint32_t anchor=*(volatile uint32_t *)(selected+8u);
  r13=*(volatile uint32_t *)((uintptr_t)existing+8u);
  if(r13<anchor){uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(anchor,r13);
   uint32_t period=*(volatile uint32_t *)((uintptr_t)existing+20u);
   uint32_t turns=opencfw_em9305_config_link_divu_prior(elapsed,period,r13)+1u;
   anchor=*(volatile uint32_t *)(selected+8u);r13+=turns*period;
  }
  uint32_t quantum=*(volatile uint32_t *)(root+4u),delta=r13-anchor;
  uint32_t span=*(volatile uint32_t *)((uintptr_t)existing+12u);
  r13=opencfw_em9305_config_link_divu_prior(delta,quantum,r13);
  uint32_t remainder=delta-quantum*r13;remainder+=span;
  uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
  fp=remainder+guard+36u;r13&=31u;goto compose_offset;
 }
 {
  uint32_t quantum=*(volatile uint32_t *)(root+4u);
  uint32_t offset=(uint16_t)index*12u;
  uintptr_t configuration=root+offset;
  uint32_t period=*(volatile uint32_t *)(configuration+52u);
  uint32_t stride=opencfw_em9305_config_link_divu_prior(period,quantum,period);
  uint32_t r16=0u,r17=0u,current=0u;
  for(uint32_t bit=0u;bit<31u;++bit){
   uint32_t run=(uint16_t)current;
   if((int32_t)run>(int32_t)r17){r17=run;r16=bit+1u;}
   current+=1u;if(((bitmap>>(bit&63u))&1u)!=0u)current=0u;
  }
  uint32_t extra=*(volatile uint32_t *)(configuration+56u);
  uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
  uint32_t r14=r16-r17;
  quantum=*(volatile uint32_t *)(root+4u);
  uint32_t total=guard+extra;
  uint32_t width_full=opencfw_em9305_config_link_divu_prior(total,quantum,total)+1u;
  uint32_t width=(uint16_t)width_full,step=(uint16_t)stride;
  uint32_t best_count=8u,best_position=0u;
  while((uint16_t)r17!=0u&&(uint8_t)best_count!=0u){
   if(action==1u){r14=r16-r17;r13=r14;}
   else if(action==2u){r16=r17+r14;r13=r16-width_full;}
   else{uint32_t start=(uint16_t)r14;r16=r17+r14;r13=(start+(uint16_t)r16)>>1;}
   uint32_t reps=1u;
   if(step!=0u)reps=opencfw_em9305_associated_slot_sdiv(32u-(uint16_t)r13,step)+1u;
   uint32_t hits=0u;
   if((uint16_t)reps!=0u){
    reps=(uint16_t)(reps-1u)+1u;
    uint32_t position=r13;
    for(uint32_t rep=0u;rep<reps;++rep){
     uint32_t bit=(uint16_t)position;
     for(uint32_t n=0u;n<width;++n,++bit)hits+=(uint32_t)((bitmap>>(bit&63u))&1u);
     position+=stride;
    }
   }
   if((uint16_t)hits<(uint8_t)best_count){best_count=hits;best_position=r13;}
   if(action!=0u)r17-=1u;else r17=(r17&0xfffeu)>>1;
  }
  if((uint8_t)best_count!=0u)r13=(uint8_t)best_position;
 }
compose_offset:
 {
  uint32_t quantum=*(volatile uint32_t *)(root+4u);
  uint32_t offset=opencfw_em9305_associated_macwhul(fp,quantum,r13);
  if(offset==0u)return incoming;
  uint32_t scheduled=*(volatile uint32_t *)(selected+8u)+offset;
  if(timestamp<scheduled){
   uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(scheduled,timestamp);
   uint32_t period=*(volatile uint32_t *)(root+(uint16_t)index*12u+52u);
   return opencfw_em9305_schedule_remu(elapsed,period);
  }
  uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(timestamp,scheduled);
  uintptr_t configuration=root+(uint16_t)index*12u;
  uint32_t period=*(volatile uint32_t *)(configuration+52u);
  uint32_t turns=opencfw_em9305_config_link_divu_prior(elapsed,period,elapsed)+1u;
  turns=(uint8_t)turns;
  uint32_t product=opencfw_em9305_native_mpywhl(period,turns);
  uint32_t adjusted=opencfw_em9305_auxiliary_elapsed_303f8c(product,timestamp);
  return adjusted+scheduled;
 }
}
