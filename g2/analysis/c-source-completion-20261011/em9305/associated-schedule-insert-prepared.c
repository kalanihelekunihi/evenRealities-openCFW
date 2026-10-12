/* Native313310 priority comparison and optional tie callback. */
uint32_t opencfw_em9305_associated_priority_313310(uintptr_t object,uintptr_t other,uintptr_t callback)
{
 uint32_t old=*(volatile uint8_t *)(other+24u),priority=*(volatile uint8_t *)(object+24u);
 if(priority<old)return 1u;
 if(callback!=0u&&priority==old)return ((uintptr_t (*)(uintptr_t,uintptr_t,uintptr_t))callback)(object,other,callback)==object;
 return 0u;
}
/* Native312da4..312f86: C basic blocks retain native list mutation/capture
 * order and subtraction N-flag tests (BP/BN), including wrapped deadlines. */
uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t object,uintptr_t tie)
{
 uintptr_t root=0x805f04u,current=*(volatile uint32_t *)(root+16u),next,previous,seek=0u,last=0u,boundary=0u;
 uint32_t success=0u,end,target,guard;
 if(current==0u)goto empty;
scan:
 end=*(volatile uint32_t *)(object+12u);end+=*(volatile uint32_t *)(object+8u);
 target=*(volatile uint32_t *)(current+8u);
 guard=opencfw_em9305_auxiliary_guard_interval();
 if((int32_t)(target-(end+guard))>=0)goto before;
 end=*(volatile uint32_t *)(current+12u);end+=*(volatile uint32_t *)(current+8u);
 target=*(volatile uint32_t *)(object+8u);
 guard=opencfw_em9305_auxiliary_guard_interval();
 if((int32_t)(target-(end+guard))<0)goto overlap;
 next=*(volatile uint32_t *)(current+4u);
 if(next!=0u){current=next;goto scan;}
 *(volatile uint32_t *)(object+4u)=0u;
 *(volatile uint32_t *)(current+4u)=(uint32_t)object;
 next=*(volatile uint32_t *)(object+4u);success=1u;
 *(volatile uint32_t *)object=(uint32_t)current;
 if(next!=0u)*(volatile uint32_t *)next=(uint32_t)object;
 else *(volatile uint32_t *)(root+20u)=(uint32_t)object;
 goto finish;
empty:
 *(volatile uint32_t *)(root+20u)=(uint32_t)object;
 *(volatile uint32_t *)(root+16u)=(uint32_t)object;
 *(volatile uint32_t *)(object+4u)=0u;*(volatile uint32_t *)object=0u;success=1u;goto finish;
before:
 if(current==*(volatile uint32_t *)(root+16u)&&*(volatile uint8_t *)root==2u)goto finish;
 previous=*(volatile uint32_t *)current;success=1u;
 *(volatile uint32_t *)object=(uint32_t)previous;
 *(volatile uint32_t *)current=(uint32_t)object;
 previous=*(volatile uint32_t *)object;
 *(volatile uint32_t *)(object+4u)=(uint32_t)current;
 if(previous!=0u)*(volatile uint32_t *)(previous+4u)=(uint32_t)object;
 else *(volatile uint32_t *)(root+16u)=(uint32_t)object;
 goto finish;
overlap:
 if(current==*(volatile uint32_t *)(root+16u)&&*(volatile uint8_t *)root==2u)goto finish;
 next=*(volatile uint32_t *)(current+4u);seek=current;
 while(next!=0u){
  end=*(volatile uint32_t *)(object+12u);end+=*(volatile uint32_t *)(object+8u);
  target=*(volatile uint32_t *)(next+8u);
  guard=opencfw_em9305_auxiliary_guard_interval();
  if((int32_t)(target-(end+guard))>=0)break;
  if(opencfw_em9305_associated_priority_313310(object,seek,tie)==0u)goto finish;
  seek=*(volatile uint32_t *)(seek+4u);
  next=*(volatile uint32_t *)(seek+4u);
 }
 if(opencfw_em9305_associated_priority_313310(object,seek,tie)==0u)goto finish;
 if(*(volatile uint32_t *)(root+16u)==current)goto replace_head;
 previous=*(volatile uint32_t *)current;last=current;boundary=0u;
 next=*(volatile uint32_t *)(previous+4u);
 while(next!=0u){
  end=*(volatile uint32_t *)(object+12u);end+=*(volatile uint32_t *)(object+8u);
  target=*(volatile uint32_t *)(next+8u);
  guard=opencfw_em9305_auxiliary_guard_interval();
  if((int32_t)(target-(end+guard))>=0){boundary=*(volatile uint32_t *)(previous+4u);goto splice_interior;}
  uintptr_t removed=*(volatile uint32_t *)(previous+4u);
  (void)opencfw_em9305_auxiliary_unlink_333804(removed);
  next=*(volatile uint32_t *)(previous+4u);last=removed;
 }
splice_interior:
 *(volatile uint32_t *)(object+4u)=(uint32_t)boundary;
 *(volatile uint32_t *)(previous+4u)=(uint32_t)object;
 next=*(volatile uint32_t *)(object+4u);
 *(volatile uint32_t *)object=(uint32_t)previous;
 if(next!=0u)*(volatile uint32_t *)next=(uint32_t)object;
 else *(volatile uint32_t *)(root+20u)=(uint32_t)object;
 goto notify_removed;
replace_head:
 next=current;last=0u;
 for(;;){
  end=*(volatile uint32_t *)(object+12u);end+=*(volatile uint32_t *)(object+8u);
  target=*(volatile uint32_t *)(next+8u);
  guard=opencfw_em9305_auxiliary_guard_interval();
  if((int32_t)(target-(end+guard))>=0){
   boundary=*(volatile uint32_t *)(root+16u);
   if(boundary!=0u){
    previous=*(volatile uint32_t *)boundary;
    *(volatile uint32_t *)(object+4u)=(uint32_t)boundary;
    *(volatile uint32_t *)object=(uint32_t)previous;
    *(volatile uint32_t *)boundary=(uint32_t)object;
    previous=*(volatile uint32_t *)object;
    if(previous!=0u)*(volatile uint32_t *)(previous+4u)=(uint32_t)object;
    else *(volatile uint32_t *)(root+16u)=(uint32_t)object;
   }else goto replace_empty;
   goto notify_removed;
  }
  last=*(volatile uint32_t *)(root+16u);
  next=*(volatile uint32_t *)(last+4u);
  *(volatile uint32_t *)(root+16u)=(uint32_t)next;
  if(next==0u){*(volatile uint8_t *)root=0u;goto replace_empty;}
  *(volatile uint32_t *)next=0u;*(volatile uint8_t *)root=0u;
 }
replace_empty:
 *(volatile uint32_t *)(root+20u)=(uint32_t)object;
 *(volatile uint32_t *)(root+16u)=(uint32_t)object;
 *(volatile uint32_t *)(object+4u)=0u;*(volatile uint32_t *)object=0u;
notify_removed:
 for(;;){
  uintptr_t callback=*(volatile uint32_t *)(current+32u);
  next=*(volatile uint32_t *)(current+4u);
  if(callback!=0u)(void)((uint32_t (*)(uintptr_t,uintptr_t))callback)(current,callback);
  uint32_t done=current==last;current=next;
  if(done!=0u)break;
 }
 success=1u;
finish:
 if(*(volatile uint32_t *)(root+16u)==object&&success!=0u){(void)opencfw_em9305_pal_timer_disarm();(void)opencfw_em9305_auxiliary_transition_333a60();}
 return success;
}
