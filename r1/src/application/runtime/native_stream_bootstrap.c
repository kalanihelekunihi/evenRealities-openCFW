#include <stdint.h>
#include "../board/native_watchdog.h"
extern void *r1_native_list_prepend(struct r1_native_list *);
/* Canonical cold-zero housekeeping48 @2001a2bc and tick callback cell4
 * @2001a2b4. Other registration fields and runtime producers remain gates. */
volatile uint32_t r1_stream_housekeeping[12] __attribute__((section(".bss.r1.stream.housekeeping"),aligned(4)));
volatile uint32_t r1_stream_tick_getter __attribute__((section(".bss.r1.stream.tick_getter"),aligned(4)));
extern uint32_t osKernelGetTickCount(void);
__attribute__((naked)) uint32_t r1_stream_tick_now(void)
{
 __asm__ volatile("ldr r0,=r1_stream_tick_getter\nldr r0,[r0]\ncmp r0,#0\nbeq 1f\nbx r0\n1: b osKernelGetTickCount\n");
}
__attribute__((naked)) uint32_t r1_stream_wake(void)
{
 __asm__ volatile("ldr r0,=r1_stream_housekeeping\nmovs r1,#0\nstr r1,[r0,#16]\nldr r1,[r0,#40]\ncmp r1,#0\nbeq 1f\nldr r0,[r0,#44]\nbx r1\n1: bx lr\n");
}
__attribute__((naked)) uint32_t r1_stream_enable(uint32_t enable __attribute__((unused)))
{
 __asm__ volatile("ldr r1,=r1_stream_housekeeping\ncmp r0,#0\nstrb r0,[r1,#12]\nbeq 1f\nb r1_stream_wake\n1: bx lr\n");
}
__attribute__((section(".text.r1_stream_keepalive"))) void r1_stream_keepalive(void){}
static __attribute__((noreturn,noinline)) void allocation_failure(void)
{
 uint32_t mask=64;
 __asm__ volatile("msr BASEPRI,%0" : : "r"(mask) : "memory");
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
__attribute__((naked)) uint32_t r1_native_stream_initialize(void)
{
 __asm__ volatile("push {r4,lr}\nmovs r1,#24\nldr r0,=r1_stream_housekeeping\nbl r1_native_list_initialize\nmovs r0,#1\nbl r1_stream_enable\npop {r4,lr}\nmovs r2,#0\nmov.w r1,#1000\nldr r0,=r1_stream_keepalive\nb r1_stream_timer_create_front\n");
}
