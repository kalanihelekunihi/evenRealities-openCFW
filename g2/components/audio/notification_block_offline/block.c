#include "block.h"
#include "../notification_wake_offline/wake.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
static void remove_item(audio_item *item){
 audio_list *list=(audio_list *)item->container;
 item->next->previous=item->previous;item->previous->next=item->next;
 if(list->index==item)list->index=item->previous;
 item->container=0;--list->count;
}
static void end_insert(audio_list *list,audio_item *item){
 audio_item *index=list->index;item->next=index;item->previous=index->previous;
 index->previous->next=item;index->previous=item;item->container=list;++list->count;
}
static void sorted_insert(audio_list *list,audio_item *item){
 audio_item *iterator=(audio_item *)&list->end_value;
 if(item->value==0xffffffffu)iterator=list->previous;
 else while(iterator->next->value<=item->value)iterator=iterator->next;
 item->next=iterator->next;item->next->previous=item;item->previous=iterator;
 iterator->next=item;item->container=list;++list->count;
}
void audio_block_current(uint32_t ticks,uint32_t indefinite){
 uint32_t now=W(0x20074a34);audio_tcb_prefix *task=(audio_tcb_prefix *)(uintptr_t)W(0x20074a20);
 remove_item(&task->state_item);
 if(ticks==0xffffffffu&&indefinite){end_insert((audio_list *)(uintptr_t)0x20073d4c,&task->state_item);return;}
 uint32_t deadline=now+ticks;task->state_item.value=deadline;
 if(deadline<now)sorted_insert((audio_list *)(uintptr_t)W(0x20074a28),&task->state_item);
 else{sorted_insert((audio_list *)(uintptr_t)W(0x20074a24),&task->state_item);if(deadline<W(0x20074a50))W(0x20074a50)=deadline;}
}
