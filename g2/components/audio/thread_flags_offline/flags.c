/* Independent449238; real original context/notify providers remain dependencies. */
#include <stdint.h>
extern int32_t audio_irq_context(void);
extern int32_t audio_notify_task(void *,uint32_t,uint32_t,uint32_t,uint32_t *);
extern int32_t audio_notify_isr(void *,uint32_t,uint32_t,uint32_t,uint32_t *,int32_t *);
uint32_t audio_thread_flags_set(void *thread,uint32_t flags){
 if(!thread || (flags&0x80000000u))return 0xfffffffcu;
 uint32_t result=0xffffffffu;
 if(audio_irq_context()){
  int32_t yield=0;(void)audio_notify_isr(thread,0,flags,1,0,&yield);
  (void)audio_notify_isr(thread,0,0,0,&result,0);
  if(yield)*(volatile uint32_t *)0xe000ed04u=0x10000000u;
 }else{
  (void)audio_notify_task(thread,0,flags,1,0);
  (void)audio_notify_task(thread,0,0,0,&result);
 }
 return result;
}
