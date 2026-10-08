#include <stdint.h>
typedef struct item{uint32_t value;struct item *next,*prev;void *owner;void *container;}item;
typedef struct list{uint32_t count;item *index;uint32_t max;item *next,*prev;}list;
extern void audio_timer_wait_enter(void),audio_timer_wait_exit(void),audio_timer_wait_unlock(void*);
extern void audio_add_current_to_delayed(uint32_t,uint32_t);
void audio_timer_restricted_wait(void *queue,uint32_t wait,uint32_t indefinite){
 uint8_t *q=queue;audio_timer_wait_enter();
 if((int8_t)q[0x44]==-1)q[0x44]=0;if((int8_t)q[0x45]==-1)q[0x45]=0;
 audio_timer_wait_exit();
 if(!*(uint32_t*)(q+0x38)){
  uint8_t *task=*(uint8_t**)0x20074a20u;item *event=(void*)(task+24);list *receivers=(void*)(q+0x24);item *at=receivers->index;
  event->next=at;event->prev=at->prev;at->prev->next=event;at->prev=event;event->container=receivers;receivers->count++;
  audio_add_current_to_delayed(indefinite?0xffffffffu:wait,indefinite);
 }
 audio_timer_wait_unlock(queue);
}
