/* Nonblocking daemon drain, contract commands3/5 and no tick wrap; no timer callback. */
#include "timer.h"
extern int32_t audio_timer_queue_receive(void*,void*,uint32_t);
extern uint32_t audio_timer_sample_time(uint32_t*);
extern uint32_t audio_timer_list_remove(void*);
extern void audio_timer_heap_free(void*);
void audio_timer_drain_stop_delete(void){
 audio_timer_message message;uint32_t overflow;
 while(audio_timer_queue_receive(*(void**)0x20074ab0u,&message,0)){
  audio_timer_prefix *timer=message.timer;
  if(timer->item.container)audio_timer_list_remove(&timer->item);
  audio_timer_sample_time(&overflow);
  if(message.command==AUDIO_TIMER_STOP)timer->status&=(uint8_t)~AUDIO_TIMER_ACTIVE;
  else if(message.command==AUDIO_TIMER_DELETE){if(timer->status&AUDIO_TIMER_STATIC)timer->status&=(uint8_t)~AUDIO_TIMER_ACTIVE;else audio_timer_heap_free(timer);}
 }
}
