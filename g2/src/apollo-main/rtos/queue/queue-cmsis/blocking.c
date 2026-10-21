/* Stock timeout/event/suspend reconstruction; no live task handover supplied. */
#include "compat.h"
extern void audio_add_current_to_delayed(uint32_t,uint32_t);
extern void audio_public_list_insert(List_t *,ListItem_t *);
void stock_timeout_capture(TimeOut_t *state){
 state->overflow=*(volatile uint32_t *)0x20074a48u;
 state->tick=*(volatile uint32_t *)0x20074a34u;
}
BaseType_t stock_timeout_check(TimeOut_t *state,TickType_t *wait){
 configASSERT(state);configASSERT(wait);
 stock_enter_critical();uint32_t now=*(volatile uint32_t *)0x20074a34u;
 uint32_t elapsed=now-state->tick;BaseType_t expired;
 if(*wait==UINT32_MAX)expired=0;
 else if(*(volatile uint32_t *)0x20074a48u!=state->overflow && now>=state->tick){*wait=0;expired=1;}
 else if(elapsed<*wait){*wait=*wait-elapsed;stock_timeout_capture(state);expired=0;}
 else{*wait=0;expired=1;}
 stock_exit_critical();return expired;
}
void stock_scheduler_suspend(void){
 volatile uint32_t *suspended=(volatile uint32_t *)0x20074a58u;
 *suspended=*suspended+1u;
}
void stock_place_event(List_t *events,TickType_t wait){
 configASSERT(events);
 uint8_t *task=*(uint8_t * volatile *)0x20074a20u;
 audio_public_list_insert(events,(ListItem_t *)(task+24));
 audio_add_current_to_delayed(wait,1);
}
void audio_queue_next_unblock(void){
 List_t *delayed=*(List_t * volatile *)0x20074a24u;
 *(volatile uint32_t *)0x20074a50u=delayed->uxNumberOfItems?delayed->xListEnd.pxNext->xItemValue:UINT32_MAX;
}
