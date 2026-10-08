/* Pending-ready resume plus accumulated tick replay; positive suspend count, coherent lists. */
#include <stdint.h>
#include "../notification_wake_offline/wake.h"
extern void audio_resume_enter(void),audio_resume_exit(void),audio_resume_yield(void),audio_resume_next_unblock(void);
static void remove_item(audio_item *item){
 audio_list *list=(audio_list*)item->container;item->next->previous=item->previous;item->previous->next=item->next;
 if(list->index==item)list->index=item->previous;item->container=0;--list->count;
}
static void ready_insert(audio_tcb_prefix *t){
 uint32_t *highest=(uint32_t*)0x20074a38u;if(*highest<t->priority)*highest=t->priority;
 audio_list *list=(audio_list*)(0x2006a49cu+20*t->priority);audio_item *index=list->index,*item=&t->state_item;
 item->next=index;item->previous=index->previous;index->previous->next=item;index->previous=item;item->container=list;list->count++;
}
extern uint32_t audio_tick_expiry_selected(void);
int32_t audio_resume_pending_ticks_selected(void){
 uint32_t *suspended=(uint32_t*)0x20074a58u;int32_t yielded=0;audio_tcb_prefix *last=0;
 audio_resume_enter();--*suspended;
 if(!*suspended&&*(uint32_t*)0x20074a30u){
  audio_list *pending=(audio_list*)0x20073d24u;
  while(pending->count){last=(audio_tcb_prefix*)pending->next->owner;remove_item(&last->event_item);remove_item(&last->state_item);ready_insert(last);
   if(last->priority>=(*(audio_tcb_prefix**)0x20074a20u)->priority)*(uint32_t*)0x20074a44u=1;
  }
  if(last)audio_resume_next_unblock();
  uint32_t *pending_ticks=(void*)0x20074a40u;
  uint32_t replay=*pending_ticks;if(replay){do{if(audio_tick_expiry_selected())*(uint32_t*)0x20074a44u=1;}while(--replay);*pending_ticks=0;}
  if(*(uint32_t*)0x20074a44u){yielded=1;audio_resume_yield();}
 }
 audio_resume_exit();return yielded;
}
