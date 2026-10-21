#include <stdint.h>
/* Exact ARM32 intrusive-list layout for the selected delayed-block provider. */
typedef struct item{uint32_t value;struct item *next,*prev;void *owner;void *container;}item;
typedef struct list{uint32_t count;item *index;uint32_t max;item *next,*prev;}list;
extern uint32_t audio_block_remove(item*);
extern void audio_block_sorted_insert(list*,item*);
void audio_add_current_to_delayed(uint32_t wait,uint32_t may_indefinite){
 uint8_t *task=*(uint8_t**)0x20074a20u;item *state=(item*)(task+4);uint32_t tick=*(uint32_t*)0x20074a34u;
 audio_block_remove(state);
 if(wait==0xffffffffu&&may_indefinite){
  list *s=(list*)0x20073d4cu;item *end=s->index;state->next=end;state->prev=end->prev;end->prev->next=state;end->prev=state;state->container=s;s->count++;return;
 }
 uint32_t wake=tick+wait;state->value=wake;
 if(wake<tick)audio_block_sorted_insert(*(list**)0x20074a28u,state);
 else{audio_block_sorted_insert(*(list**)0x20074a24u,state);if(wake<*(uint32_t*)0x20074a50u)*(uint32_t*)0x20074a50u=wake;}
}
