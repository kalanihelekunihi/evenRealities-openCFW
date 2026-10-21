/* Independent selected generic ISR notify: index0, actions0/1 only.
 * Caller supplies valid/coherent TCBs/list state; this is not the full API. */
#include "wake.h"
extern uint32_t audio_mask_save(void);
extern void audio_mask_restore(uint32_t);
static void remove_item(audio_item *p){audio_list *list=p->container;p->next->previous=p->previous;p->previous->next=p->next;if(list->index==p)list->index=p->previous;p->container=0;list->count--;}
static void insert_item(audio_list *list,audio_item *p){audio_item *index=list->index;p->next=index;p->previous=index->previous;index->previous->next=p;index->previous=p;p->container=list;list->count++;}
int32_t audio_notify_isr(void *handle,uint32_t index,uint32_t value,uint32_t action,uint32_t *previous,int32_t *yield){
 audio_tcb_prefix *t=handle;(void)index;uint32_t saved=audio_mask_save();
 if(previous)*previous=t->notification;uint8_t old=t->notification_state;t->notification_state=2;
 if(action==1)t->notification|=value;
 if(old==1){
  if(*(volatile uint32_t *)0x20074a58u==0){remove_item(&t->state_item);volatile uint32_t *highest=(volatile uint32_t *)0x20074a38u;if(t->priority>*highest)*highest=t->priority;insert_item((audio_list *)(0x2006a49cu+t->priority*20),&t->state_item);}
  else insert_item((audio_list *)0x20073d24u,&t->event_item);
  audio_tcb_prefix *current=*(audio_tcb_prefix **)0x20074a20u;
  if(t->priority>current->priority){if(yield)*yield=1;*(volatile uint32_t *)0x20074a44u=1;}
 }
 audio_mask_restore(saved);return 1;
}
