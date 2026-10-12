/* Authenticated ARC native 3336d8 bitmap, 33382c occupancy, 3338f4 setter,
 * 333948 selector and 3133b4 allocator. Source reduction, not runtime admission. */
static inline uint32_t opencfw_em9305_associated_slot_sdiv(uint32_t numerator,uint32_t denominator)
{uint32_t result;result=(uint32_t)((int32_t)numerator/(int32_t)denominator);return result;}
static inline uint32_t opencfw_em9305_associated_slot_rem625(uint32_t value)
{uint32_t result;result=value%625u;return result;}
uint64_t opencfw_em9305_associated_bitmap_3336d8(uintptr_t head,uint32_t special)
{
 if(head==0u)return 0u;
 uint32_t quantum=*(volatile uint32_t *)(uintptr_t)0x805f2cu;
 uint64_t bits=0u;
 for(uintptr_t node=head;node!=0u;node=*(volatile uint32_t *)(node+4u)){
  uint32_t period=*(volatile uint32_t *)(node+20u);
  if(period==0u)continue;
  if(*(volatile uint8_t *)(node+25u)==1u&&special==0u)continue;
  uint32_t delta=*(volatile uint32_t *)(node+8u)-*(volatile uint32_t *)(head+8u);
  uint32_t end=*(volatile uint32_t *)(node+12u)+delta;
  uint32_t endq=opencfw_em9305_config_link_divu_prior(end,quantum,end);
  if((endq&224u)!=0u)break;
  uint32_t pq=opencfw_em9305_config_link_divu_prior(period,quantum,period);
  uint32_t start=opencfw_em9305_config_link_divu_prior(delta,quantum,delta);
  uint32_t stride=(uint8_t)pq,reps=1u;
  if(stride!=0u)reps=(uint8_t)(opencfw_em9305_associated_slot_sdiv(32u-(uint8_t)start,stride)+1);
  uint32_t width=(uint8_t)(endq-start+1u);
  for(uint32_t rep=0u;rep<reps;++rep){
   start=(uint8_t)start;
   for(uint32_t offset=0u;offset<width;++offset)bits|=UINT64_C(1)<<((start+offset)&63u);
   start+=stride;
  }
 }
 return bits;
}
uint32_t opencfw_em9305_associated_available_33382c(uint32_t id,uint32_t value,uint32_t extent,uint32_t existing)
{
 uintptr_t root=0x805f28u;
 if(*(volatile uint8_t *)root==0u)return 1u;
 uintptr_t node=*(volatile uint32_t *)(uintptr_t)0x805f14u;
 while(node!=0u&&*(volatile uint32_t *)(node+20u)==0u)node=*(volatile uint32_t *)(node+4u);
 uint64_t bits=opencfw_em9305_associated_bitmap_3336d8(node,1u);
 uint32_t quantum,occupied=0u;
 while(bits!=0u){quantum=*(volatile uint32_t *)(root+4u);occupied+=(0u-(uint32_t)(bits&1u))&quantum;bits>>=1u;}
 if(existing!=0u){
  uintptr_t slot=root+(id&65535u)*12u;
  if(*(volatile uint8_t *)(slot+48u)==id){
   uint32_t oldextent=*(volatile uint32_t *)(slot+56u);
   uint32_t overhead=opencfw_em9305_auxiliary_guard_interval();
   uint32_t oldvalue=*(volatile uint32_t *)(slot+52u);
   quantum=*(volatile uint32_t *)(root+4u);
   uint32_t ratio=(uint8_t)opencfw_em9305_config_link_divu_prior(oldvalue,quantum,quantum);
   uint32_t contribution=(overhead+oldextent)*(ratio!=0u?opencfw_em9305_config_link_divu_prior(32u,ratio,32u):1u);
   uint32_t reduced=occupied-contribution;
   occupied=occupied<reduced?0u:reduced;
  }
 }
 uint32_t overhead=opencfw_em9305_auxiliary_guard_interval();
 quantum=*(volatile uint32_t *)(root+4u);
 uint32_t ratio=(uint8_t)opencfw_em9305_config_link_divu_prior(value,quantum,value);
 uint32_t total=occupied+(overhead+extent)*(ratio!=0u?opencfw_em9305_config_link_divu_prior(32u,ratio,32u):1u);
 return total<(quantum<<5u);
}
uint32_t opencfw_em9305_associated_set_3338f4(uint32_t id,uint32_t value,uint32_t extent)
{
 uintptr_t root=0x805f28u,slot=root+(id&65535u)*12u;
 uint32_t current=*(volatile uint32_t *)(root+8u);
 if(current==0u){(void)opencfw_em9305_radio_primary_timer_333bec(value);*(volatile uint8_t *)(slot+49u)=1u;}
 else if(current==value)*(volatile uint8_t *)(slot+49u)=1u;
 else if(opencfw_em9305_associated_slot_rem625(value)!=0u)*(volatile uint8_t *)(slot+49u)=0u;
 else {if(current<value)(void)opencfw_em9305_radio_primary_timer_333bec(value);*(volatile uint8_t *)(slot+49u)=1u;}
 *(volatile uint32_t *)(slot+56u)=extent;
 *(volatile uint32_t *)(slot+52u)=value;
 *(volatile uint8_t *)(slot+48u)=(uint8_t)id;
 return (uint32_t)slot;
}
uint32_t opencfw_em9305_associated_select_333948(uint32_t minimum,uint32_t maximum,uint32_t step,uint32_t direction,uint32_t exclude)
{
 uint32_t quotient=opencfw_em9305_config_link_divu_prior(direction==1u?maximum:minimum,625u,0u);
 if(step>=626u)quotient=opencfw_em9305_config_link_divu_prior(quotient,opencfw_em9305_config_link_divu_prior(step,625u,625u),quotient);
 uint32_t threshold=quotient*step;
 if(direction==1u){if(threshold<minimum)threshold=maximum;}
 else if(threshold<minimum)threshold=(quotient+1u)*step;
 uint32_t largest=0u;
 for(uint32_t index=0u;index<8u;++index){
  if(index==exclude)continue;
  uint32_t value=*(volatile uint32_t *)(uintptr_t)(0x805f38u+index*4u);
  if(value>=threshold&&value<=maximum&&value>=largest)largest=value;
 }
 if(largest!=0u)return largest;
 return maximum<threshold?maximum:threshold;
}
uint32_t opencfw_em9305_associated_slot_allocate_3133b4(uint32_t id,uint32_t direction,uint32_t minimum,uint32_t maximum,uint32_t extent,uintptr_t output,uintptr_t callback)
{
 (void)callback; /* Native passes R6 but all three children leave it unused. */
 uint32_t choice=opencfw_em9305_associated_select_333948(minimum,maximum,625u,direction,id);
 if(opencfw_em9305_associated_available_33382c(id,choice,extent,0u)==0u)return 0u;
 (void)opencfw_em9305_associated_set_3338f4(id,choice,extent);
 uintptr_t root=0x805f28u;
 uint32_t count=*(volatile uint8_t *)root;
 *(volatile uint32_t *)(root+16u+id*4u)=choice;
 *(volatile uint8_t *)root=(uint8_t)(count+1u);
 if(output!=0u)*(volatile uint32_t *)output=choice;
 return 1u;
}
