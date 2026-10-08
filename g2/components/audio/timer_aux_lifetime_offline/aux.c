/* CMSIS timer adapter and due-single-shot prefix; actual kernel peers retained. */
#include <stdint.h>
#include "../timer_commands_offline/timer.h"
extern int32_t audio_aux_irq_context(void);
extern uint32_t audio_aux_get_id(audio_timer_prefix*);
extern int32_t audio_aux_command(audio_timer_prefix*,int32_t,uint32_t,void*,uint32_t);
extern void audio_aux_free(void*),audio_aux_suspend(void),audio_aux_resume(void);
extern uint32_t audio_aux_sample_time(uint32_t*),audio_aux_list_remove(void*);
typedef struct {void(*callback)(void*);void *argument;} audio_aux_callback;
int32_t audio_timer_delete_selected(audio_timer_prefix *timer){
 if(audio_aux_irq_context())return -6;if(!timer)return -4;
 uint32_t id=audio_aux_get_id(timer);
 if(audio_aux_command(timer,5,0,0,0)!=1)return -3;
 if(id&1)audio_aux_free((void*)(id&~1u));
 return 0;
}
void audio_timer_callback_selected(audio_timer_prefix *timer){
 audio_aux_callback *cb=(audio_aux_callback*)(audio_aux_get_id(timer)&~1u);
 if(cb)cb->callback(cb->argument);
}
void audio_timer_due_single_selected(uint32_t expiry,uint32_t list_empty){
 /* Contract: no time wrap, list nonempty, single-shot head is due. Other branches excluded. */
 uint32_t switched;audio_aux_suspend();uint32_t now=audio_aux_sample_time(&switched);
 if(switched||list_empty||now<expiry){audio_aux_resume();return;}
 audio_aux_resume();uint32_t *list=*(uint32_t**)0x20074aa8u;
 audio_timer_list_item *head=(audio_timer_list_item*)list[3];audio_timer_prefix *timer=(audio_timer_prefix*)head->owner;
 audio_aux_list_remove(&timer->item);timer->status&=(uint8_t)~AUDIO_TIMER_ACTIVE;
 audio_timer_callback_selected(timer);
}
/* Minimum requested block size only; a small remainder can cause a larger whole-block allocation. */
uint32_t audio_heap_minimum_block(uint32_t payload){
 if(!payload)return 0;uint32_t extra=16-(payload&7u);
 if(payload>0xffffffffu-extra)return 0;uint32_t wanted=payload+extra;
 return wanted&0x80000000u?0:wanted;
}
