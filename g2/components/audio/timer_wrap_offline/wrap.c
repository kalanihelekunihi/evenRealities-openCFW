#include <stdint.h>
extern uint32_t audio_timer_wrap_get_tick(void);
extern void audio_timer_wrap_expire(uint32_t,uint32_t);
void audio_timer_switch_lists_selected(void){
 uint32_t **current=(void*)0x20074aa8u,**overflow=(void*)0x20074aacu;
 while((*current)[0])audio_timer_wrap_expire(**(uint32_t**)(*current+3),0xffffffffu);
 uint32_t *old=*current;*current=*overflow;*overflow=old;
}
uint32_t audio_timer_sample_time_selected(uint32_t *switched){
 uint32_t now=audio_timer_wrap_get_tick();uint32_t *last=(void*)0x20074ab8u;
 if(now<*last){audio_timer_switch_lists_selected();*switched=1;}else *switched=0;
 *last=now;return now;
}
