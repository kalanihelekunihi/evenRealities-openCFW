#include <stdint.h>
typedef struct item{uint32_t value;struct item *next,*prev;uint8_t *owner;void *container;}item;
typedef struct list{uint32_t count;item *index;uint32_t max;item *next,*prev;}list;
static void remove_item(item *i){list *l=i->container;i->next->prev=i->prev;i->prev->next=i->next;if(l->index==i)l->index=i->prev;i->container=0;l->count--;}
static void append_index(list *l,item *i){item *at=l->index;i->next=at;i->prev=at->prev;at->prev->next=i;at->prev=i;i->container=l;l->count++;}
uint32_t audio_tick_expiry_selected(void){
 if(*(uint32_t*)0x20074a58u){(*(uint32_t*)0x20074a40u)++;return 0;}
 uint32_t tick=++*(uint32_t*)0x20074a34u,need=0;list **delayed=(void*)0x20074a24u,**overflow=(void*)0x20074a28u;
 if(!tick){/* Contract: old delayed list empty at wrap, matching kernel invariant. */
  list *old=*delayed;*delayed=*overflow;*overflow=old;(*(uint32_t*)0x20074a48u)++;
  *(uint32_t*)0x20074a50u=(*delayed)->count?(*delayed)->next->value:0xffffffffu;
 }
 uint32_t *next=(void*)0x20074a50u;
 if(tick>=*next){
  for(;;){
   if(!(*delayed)->count){*next=0xffffffffu;break;}
   uint8_t *task=(*delayed)->next->owner;item *state=(void*)(task+4),*event=(void*)(task+24);
   if(tick<state->value){*next=state->value;break;}
   remove_item(state);if(event->container)remove_item(event);
   uint32_t priority=*(uint32_t*)(task+0x2c);if(priority>*(uint32_t*)0x20074a38u)*(uint32_t*)0x20074a38u=priority;
   append_index((list*)(0x2006a49cu+20*priority),state);
   uint8_t *current=*(uint8_t**)0x20074a20u;if(priority>*(uint32_t*)(current+0x2c))need=1;
  }
 }
 uint8_t *current=*(uint8_t**)0x20074a20u;list *ready=(void*)(0x2006a49cu+20*(*(uint32_t*)(current+0x2c)));
 if(ready->count>=2||*(uint32_t*)0x20074a44u)need=1;return need;
}
