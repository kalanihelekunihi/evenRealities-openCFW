#include <stdint.h>
#include "../board/native_watchdog.h"
extern volatile uint32_t r1_stream_housekeeping[12];
extern uint32_t r1_stream_tick_now(void);
extern void r1_native_list_set_next(struct r1_native_list *,void *,void *);
extern void r1_native_list_set_previous(struct r1_native_list *,void *,void *);
extern uint32_t vPortFree(void *);
typedef uint32_t (*timer_callback)(volatile uint32_t *);
static __attribute__((noreturn,noinline)) void bad_timer(void)
{uint32_t mask=64;__asm__ volatile("msr BASEPRI,%0"::"r"(mask):"memory");*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;for(;;){}}
uint32_t r1_stream_ticks_elapsed(uint32_t before){return r1_stream_tick_now()-before;}
uint32_t r1_stream_timer_remaining(volatile uint32_t *timer)
{uint32_t elapsed=r1_stream_ticks_elapsed(timer[1]);uint32_t period=timer[0];return period<=elapsed?0:period-elapsed;}
/* Native5d998 unlinks without freeing. The release entry owns deallocation. */
void r1_stream_list_unlink(struct r1_native_list *list,void *node)
{
 if(!list)return;
 if(r1_native_list_head(list)==node){
  void *next=r1_native_list_next(list,node);list->head=next;
  if(next)r1_native_list_set_previous(list,next,0);else list->tail=0;
 }else if(list->tail==node){
  void *previous=*(void **)((uintptr_t)node+list->payload_bytes);list->tail=previous;
  if(previous)r1_native_list_set_next(list,previous,0);else list->head=0;
 }else{
  void *previous=*(void **)((uintptr_t)node+list->payload_bytes);
  void *next=r1_native_list_next(list,node);
  r1_native_list_set_next(list,previous,next);r1_native_list_set_previous(list,next,previous);
 }
}
uint32_t r1_stream_timer_release(volatile uint32_t *timer)
{
 if(!timer)bad_timer();
 r1_stream_list_unlink((struct r1_native_list *)(uintptr_t)r1_stream_housekeeping,(void *)(uintptr_t)timer);
 ((volatile uint8_t *)r1_stream_housekeeping)[14]=1;
 return vPortFree((void *)(uintptr_t)timer);
}
uint32_t r1_stream_timer_stop(volatile uint32_t *timer)
{if(!timer)bad_timer();timer[5]|=1;return (uint32_t)(uintptr_t)timer;}
uint32_t r1_stream_timer_expire(volatile uint32_t *timer)
{
 if(((volatile uint8_t *)timer)[20]&1)return 0;
 uint32_t fired=0;
 if(!r1_stream_timer_remaining(timer)){
  uint32_t repeat=timer[4];if((int32_t)repeat>0)timer[4]=repeat-1;
  timer[1]=r1_stream_tick_now();uint32_t callback=timer[2];
  if(callback && repeat)(void)((timer_callback)(uintptr_t)callback)(timer);
  fired=1;
 }
 if(!((volatile uint8_t *)r1_stream_housekeeping)[14] && !timer[4]){
  if(((volatile uint8_t *)timer)[20]&2)(void)r1_stream_timer_release(timer);
  else (void)r1_stream_timer_stop(timer);
 }
 return fired;
}
uint32_t r1_native_sensor_timer_poll(void)
{
 volatile uint8_t *bytes=(volatile uint8_t *)r1_stream_housekeeping;
 if(bytes[20])return 1;
 bytes[20]=1;
 if(!bytes[12]){bytes[20]=0;return 1;}
 uint32_t start=r1_stream_tick_now();
 if(!start){uint32_t count=r1_stream_housekeeping[9]+1;r1_stream_housekeeping[9]=count;if(count>100)r1_stream_housekeeping[9]=0;}
 struct r1_native_list *list=(struct r1_native_list *)(uintptr_t)r1_stream_housekeeping;
 for(;;){
  bytes[14]=0;bytes[15]=0;
  volatile uint32_t *timer=r1_native_list_head(list);
  while(timer){
   volatile uint32_t *next=r1_native_list_next(list,(void *)(uintptr_t)timer);
   if(r1_stream_timer_expire(timer) && (bytes[15] || bytes[14]))break;
   timer=next;
  }
  if(!timer)break;
 }
 uint32_t minimum=UINT32_MAX;
 for(volatile uint32_t *timer=r1_native_list_head(list);timer;timer=r1_native_list_next(list,(void *)(uintptr_t)timer)){
  if(!(((volatile uint8_t *)timer)[20]&1)){uint32_t remain=r1_stream_timer_remaining(timer);if(remain<minimum)minimum=remain;}
 }
 r1_stream_housekeeping[7]+=r1_stream_ticks_elapsed(start);
 uint32_t span=r1_stream_ticks_elapsed(r1_stream_housekeeping[8]);
 if(span>=500){
  uint8_t percent=(uint8_t)((r1_stream_housekeeping[7]*100u)/span);
  bytes[13]=percent>100?0:(uint8_t)(100-percent);r1_stream_housekeeping[7]=0;
  r1_stream_housekeeping[8]=r1_stream_tick_now();
 }
 r1_stream_housekeeping[4]=minimum;bytes[20]=0;return minimum;
}
