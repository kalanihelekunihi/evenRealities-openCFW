/* Native schedule313220..3132f8; source-owned time and guard providers.
 * Signed native CMP.N is the sign bit of wrapping32-bit subtraction. */
uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t object)
{
 uintptr_t root=0x805f04u,queue=root+16u;
 uint32_t now=opencfw_em9305_pal_current_time();
 uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
 uintptr_t head=*(volatile uint32_t *)queue;
 *(volatile uint32_t *)(object+8u)=guard+now;
 if(head==0u){
  *(volatile uint32_t *)(queue+4u)=(uint32_t)object;
  *(volatile uint32_t *)queue=(uint32_t)object;
  *(volatile uint32_t *)(object+4u)=0u;
  *(volatile uint32_t *)object=0u;
  goto done;
 }
 uint32_t width=*(volatile uint32_t *)(object+12u);
 uint32_t head_time=*(volatile uint32_t *)(head+8u);
 guard=opencfw_em9305_auxiliary_guard_interval();
 width+=guard;
 uint32_t edge=guard+width;
 if(((head_time-edge)&0x80000000u)==0u&&*(volatile uint8_t *)root!=2u){
  head=*(volatile uint32_t *)queue;
  uintptr_t prior=*(volatile uint32_t *)head;
  *(volatile uint32_t *)object=(uint32_t)prior;
  *(volatile uint32_t *)head=(uint32_t)object;
  prior=*(volatile uint32_t *)object;
  *(volatile uint32_t *)(object+4u)=(uint32_t)head;
  if(prior!=0u)*(volatile uint32_t *)(prior+4u)=(uint32_t)object;
  else *(volatile uint32_t *)queue=(uint32_t)object;
  goto done;
 }
 uintptr_t link=queue,current;
 for(;;){
  current=*(volatile uint32_t *)link;
  head=*(volatile uint32_t *)queue;
  uint32_t end;
  if(current==head){
   end=*(volatile uint32_t *)(current+16u);
   if(end!=0u)end+=*(volatile uint32_t *)(current+8u);
   else {
    uint32_t start=*(volatile uint32_t *)(current+8u);
    end=*(volatile uint32_t *)(current+12u)+start;
   }
  }else{
   uint32_t start=*(volatile uint32_t *)(current+8u);
   end=*(volatile uint32_t *)(current+12u)+start;
  }
  guard=opencfw_em9305_auxiliary_guard_interval();
  uintptr_t next=*(volatile uint32_t *)(current+4u);
  uint32_t time=guard+end;
  *(volatile uint32_t *)(object+8u)=time;
  uintptr_t after=0u;
  if(next!=0u){
   uint32_t needed=*(volatile uint32_t *)(object+12u);
   uint32_t next_time=*(volatile uint32_t *)(next+8u);
   link=current+4u;
   uint32_t sum=time+needed;
   guard=opencfw_em9305_auxiliary_guard_interval();
   sum+=guard;
   if(((next_time-sum)&0x80000000u)!=0u)continue;
   after=*(volatile uint32_t *)link;
  }
  *(volatile uint32_t *)(object+4u)=(uint32_t)after;
  *(volatile uint32_t *)(current+4u)=(uint32_t)object;
  after=*(volatile uint32_t *)(object+4u);
  *(volatile uint32_t *)object=(uint32_t)current;
  if(after!=0u)*(volatile uint32_t *)after=(uint32_t)object;
  else *(volatile uint32_t *)(root+20u)=(uint32_t)object;
  break;
 }
 done:
 head=*(volatile uint32_t *)queue;
 if(head==object)return opencfw_em9305_auxiliary_transition_333a60();
 return (uint32_t)head;
}
