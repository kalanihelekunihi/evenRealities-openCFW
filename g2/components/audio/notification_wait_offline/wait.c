/* Selected index0 notify wait and CMSIS wait wrapper. Block/yield remain peers. */
#include <stdint.h>
#include "../notification_wake_offline/wake.h"
extern void audio_enter_critical(void),audio_exit_critical(void),audio_yield(void);
extern void audio_block_ticks(uint32_t,uint32_t);
extern uint32_t audio_tick(void);
extern int32_t audio_irq_context(void);
int32_t audio_notify_wait(uint32_t index,uint32_t clear_enter,uint32_t clear_exit,uint32_t *out,uint32_t ticks){
 (void)index;audio_tcb_prefix *t=*(audio_tcb_prefix **)0x20074a20u;audio_enter_critical();
 if(t->notification_state!=2){t->notification&=~clear_enter;t->notification_state=1;if(ticks){audio_block_ticks(ticks,1);audio_yield();}}
 audio_exit_critical();audio_enter_critical();if(out)*out=t->notification;
 int32_t result=t->notification_state==2;if(result)t->notification&=~clear_exit;t->notification_state=0;audio_exit_critical();return result;
}
uint32_t audio_flags_wait(uint32_t requested,uint32_t options,uint32_t timeout){
 if(audio_irq_context())return 0xfffffffau;if(requested&0x80000000u)return 0xfffffffcu;
 uint32_t clear=(options&2)?0:requested,result=0,start=audio_tick(),remaining=timeout,observed;
 for(;;){int32_t ok=audio_notify_wait(0,0,clear,&observed,remaining);
  if(!ok)return timeout?0xfffffffeu:0xfffffffdu;
  result=(result&requested)|observed;
  if((options&1)?((result&requested)==requested):((result&requested)!=0))return result;
  if(!timeout)return 0xfffffffdu;uint32_t elapsed=audio_tick()-start;remaining=timeout<elapsed?0:timeout-elapsed;
 }
}
