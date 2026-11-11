#include <stdint.h>
#include "../board/native_watchdog.h"
extern void *r1_native_list_prepend(struct r1_native_list *),*r1_native_list_append(struct r1_native_list *);
/* Canonical cold-zero housekeeping48 @2001a2bc and tick callback cell4
 * @2001a2b4. Other registration fields and runtime producers remain gates. */
volatile uint32_t r1_stream_housekeeping[12] __attribute__((section(".bss.r1.stream.housekeeping"),aligned(4)));
volatile uint32_t r1_stream_tick_getter __attribute__((section(".bss.r1.stream.tick_getter"),aligned(4)));
extern uint32_t osKernelGetTickCount(void);
/* Native dispatch leaves 0x8a1d0, 0x8a540 and 0x8a3f0. Shared loads
 * remain volatile and ordered; callback return values are not discarded. */
uint32_t r1_stream_tick_now(void)
{
 uint32_t callback=r1_stream_tick_getter;
 if (callback) return ((uint32_t (*)(void))(uintptr_t)callback)();
 return osKernelGetTickCount();
}
uint32_t r1_stream_wake(void)
{
 r1_stream_housekeeping[4]=0;
 uint32_t callback=r1_stream_housekeeping[10];
 if (callback) {
  uint32_t context=r1_stream_housekeeping[11];
  return ((uint32_t (*)(uint32_t))(uintptr_t)callback)(context);
 }
 return (uint32_t)(uintptr_t)r1_stream_housekeeping;
}
uint32_t r1_stream_enable(uint32_t enable)
{
 ((volatile uint8_t *)r1_stream_housekeeping)[12]=(uint8_t)enable;
 if (enable) return r1_stream_wake();
 return 0;
}
__attribute__((section(".text.r1_stream_keepalive"))) void r1_stream_keepalive(void){}
static __attribute__((noreturn,noinline)) void allocation_failure(void)
{
 uint32_t mask=64;
 __builtin_arm_wsr("basepri",mask);
 *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
 for(;;){}
}
uint32_t r1_stream_timer_create_front(uint32_t callback,uint32_t period,uint32_t context)
{
 volatile uint32_t *timer=r1_native_list_prepend((struct r1_native_list *)(uintptr_t)r1_stream_housekeeping);
 if(!timer)allocation_failure();
 timer[2]=callback;timer[0]=period;timer[4]=UINT32_MAX;
 timer[5]&=~UINT32_C(1);
 uint32_t now=r1_stream_tick_now();timer[3]=context;timer[1]=now;
 timer[5]|=2;
 ((volatile uint8_t *)r1_stream_housekeeping)[15]=1;
 (void)r1_stream_wake();return (uint32_t)(uintptr_t)timer;
}
/* Native 0x8a368 appends, preserving an existing timer list head. */
uint32_t r1_stream_timer_create_back(uint32_t callback,uint32_t period,uint32_t context)
{
 volatile uint32_t *timer=r1_native_list_append((struct r1_native_list *)(uintptr_t)r1_stream_housekeeping);
 if(!timer)allocation_failure();
 timer[2]=callback;timer[0]=period;timer[4]=UINT32_MAX;
 timer[5]&=~UINT32_C(1);
 uint32_t now=r1_stream_tick_now();timer[3]=context;timer[1]=now;
 timer[5]|=2;
 ((volatile uint8_t *)r1_stream_housekeeping)[15]=1;
 (void)r1_stream_wake();return (uint32_t)(uintptr_t)timer;
}
/* Native 0x8a55c initializes the list before enabling and creating its timer. */
uint32_t r1_native_stream_initialize(void)
{
 r1_native_list_initialize((struct r1_native_list *)(uintptr_t)r1_stream_housekeeping,24);
 (void)r1_stream_enable(1);
 return r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_stream_keepalive,1000,0);
}
