/* Complete native312f88..3130d2. BN/BP test wrapped subtraction N;
 * list links are native previous@0,next@4. No invented iteration cap. */
uint32_t opencfw_em9305_init_schedule_adjust_312f88(uintptr_t object,uint32_t minimum,uint32_t maximum)
{
 uintptr_t root=0x805f04u,list=root+16u,node=0u,neighbor=0u,link=0u;
 uint32_t original=*(volatile uint32_t *)(object+8u),candidate=original+minimum;
 *(volatile uint32_t *)(object+8u)=candidate;
 uint32_t now=opencfw_em9305_pal_current_time();
 if(opencfw_em9305_auxiliary_elapsed_303f8c(*(volatile uint32_t *)(object+8u),now+25u)==0u){
  if((maximum&0x80000000u)==0u)goto fail;
  now=opencfw_em9305_pal_current_time();
  original=now+opencfw_em9305_auxiliary_guard_interval();
  *(volatile uint32_t *)(object+8u)=original;
 }
 node=*(volatile uint32_t *)list;
 if(node==0u){
  *(volatile uint32_t *)(list+4u)=(uint32_t)object;
  *(volatile uint32_t *)list=(uint32_t)object;
  *(volatile uint32_t *)(object+4u)=0u;
  *(volatile uint32_t *)object=0u;
  goto success;
 }
 candidate=*(volatile uint32_t *)(object+8u);
 uint32_t headtime=*(volatile uint32_t *)(node+8u);
 if(((headtime-candidate)&0x80000000u)==0u){
  uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
  uint32_t end=candidate+guard+guard;
  if(((headtime-end)&0x80000000u)==0u&&*(volatile uint8_t *)root!=2u){
   neighbor=*(volatile uint32_t *)(root+16u);goto insert_before;
  }
  candidate=*(volatile uint32_t *)(object+8u);
 }
 node=*(volatile uint32_t *)(root+20u);
 uint32_t time=*(volatile uint32_t *)(node+8u);
 uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
 uint32_t end=time+guard+guard;
 if(((candidate-end)&0x80000000u)==0u){
  neighbor=*(volatile uint32_t *)(root+20u);
  *(volatile uint32_t *)object=(uint32_t)neighbor;
  link=*(volatile uint32_t *)(neighbor+4u);
  *(volatile uint32_t *)(object+4u)=(uint32_t)link;
  *(volatile uint32_t *)(neighbor+4u)=(uint32_t)object;
  link=*(volatile uint32_t *)(object+4u);
  goto update_next;
 }
 link=list;
scan:
 node=*(volatile uint32_t *)link;
 if(node==0u)goto fail;
 time=*(volatile uint32_t *)(node+8u);
 candidate=*(volatile uint32_t *)(object+8u);
 guard=opencfw_em9305_auxiliary_guard_interval();
 end=time+guard+guard;
 if(((candidate-end)&0x80000000u)!=0u){
  time=*(volatile uint32_t *)(node+8u);
  guard=opencfw_em9305_auxiliary_guard_interval();
  candidate=time+guard+guard;
  *(volatile uint32_t *)(object+8u)=candidate;
 }else candidate=*(volatile uint32_t *)(object+8u);
 uint32_t displacement=candidate-original;
 if(displacement<minimum||maximum<displacement)goto advance;
 neighbor=*(volatile uint32_t *)(node+4u);
 if(neighbor==0u){
  *(volatile uint32_t *)(object+4u)=0u;
  *(volatile uint32_t *)(node+4u)=(uint32_t)object;
  link=*(volatile uint32_t *)(object+4u);
  *(volatile uint32_t *)object=(uint32_t)node;
  goto update_next;
 }
 time=*(volatile uint32_t *)(neighbor+8u);
 uint32_t duration=*(volatile uint32_t *)(object+12u);
 guard=opencfw_em9305_auxiliary_guard_interval();
 end=duration+guard+guard;
 if(((time-end)&0x80000000u)==0u){neighbor=*(volatile uint32_t *)(node+4u);goto insert_before;}
advance:
 link=node+4u;goto scan;
insert_before:
 link=*(volatile uint32_t *)neighbor;
 *(volatile uint32_t *)object=(uint32_t)link;
 *(volatile uint32_t *)neighbor=(uint32_t)object;
 link=*(volatile uint32_t *)object;
 *(volatile uint32_t *)(object+4u)=(uint32_t)neighbor;
 if(link==0u)*(volatile uint32_t *)(root+16u)=(uint32_t)object;
 else *(volatile uint32_t *)(link+4u)=(uint32_t)object;
 goto success;
update_next:
 if(link==0u)*(volatile uint32_t *)(root+20u)=(uint32_t)object;
 else *(volatile uint32_t *)link=(uint32_t)object;
success:
 if(*(volatile uint32_t *)list==(uint32_t)object)(void)opencfw_em9305_auxiliary_transition_333a60();
 return 1u;
fail:
 *(volatile uint32_t *)(object+8u)=original;return 0u;
}
