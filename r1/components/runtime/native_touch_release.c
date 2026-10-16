#include <stdint.h>
#include "../board/native_battery_memory.h"
extern void __aeabi_memclr(void *,uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern uint32_t r1_touch_gesture_dispatch_boundary(const void *);
extern uint32_t r1_touch_task_message_boundary(const void *);
/* Complete cleared span, with interpretation limited to authenticated offsets. */
volatile uint8_t r1_touch_contact_state[100] __attribute__((section(".r1.touch.contact"),aligned(4)))={0};
volatile uint8_t r1_touch_release_timer_pending __attribute__((section(".r1.touch.timer_pending")))=0;
volatile uint8_t r1_touch_synthetic_flag __attribute__((section(".r1.touch.synthetic_flag")))=0;
__attribute__((used,noinline)) static uint32_t release_timer_kernel(volatile uint8_t *frame)
{
 __aeabi_memclr((void *)(uintptr_t)frame,44);
 write32(frame+4,5);write32(frame+8,0);
 return r1_touch_task_message_boundary((const void *)(uintptr_t)frame);
}
__attribute__((naked,noinline,section(".r1.touch.release.timer_code"))) void r1_touch_release_timer_callback(uint32_t argument __attribute__((unused)))
{__asm__ volatile("push {lr}\nsub sp,sp,#44\nmov r0,sp\nbl release_timer_kernel\nadd sp,sp,#44\npop {pc}");}
/* 64-bit return is an internal bridge signal: high word requests clear after
 * restoring the external frame; low word is the native inactive return byte. */
__attribute__((used,noinline)) static uint64_t synthetic_release_kernel(volatile uint32_t *frame)
{
 uint32_t active=r1_touch_contact_state[36];if(active!=1)return active;
 if(r1_touch_release_timer_pending){
  (void)r1_native_delayed_cancel(r1_touch_release_timer_callback,0);
  r1_touch_release_timer_pending=0;
 }
 if(r1_touch_contact_state[8]!=1){
  frame[0]=2;r1_touch_synthetic_flag=1;
  (void)r1_touch_gesture_dispatch_boundary((const void *)(uintptr_t)frame);
 }else{
  int32_t delta=(int32_t)r1_touch_contact_state[37]-(int32_t)r1_touch_contact_state[60];
  uint32_t direction=delta<0?32u:64u;
  if(!delta)direction=(int8_t)r1_touch_contact_state[96]<0?32u:64u;
  uint32_t distance=(uint32_t)(delta<0?-delta:delta);
  if(distance>255)distance=255;if(!distance)distance=1;
  uint32_t velocity=r1_touch_contact_state[95];if(!velocity)velocity=1;
  frame[0]=(direction|2u)|(distance<<8)|(velocity<<16);
  (void)r1_touch_gesture_dispatch_boundary((const void *)(uintptr_t)frame);
  frame[1]=2;r1_touch_synthetic_flag=1;
  (void)r1_touch_gesture_dispatch_boundary((const void *)(uintptr_t)(frame+1));
 }
 r1_touch_synthetic_flag=0;
 return UINT64_C(1)<<32;
}
__attribute__((used,noinline)) static uint32_t contact_clear_result(void)
{
 __aeabi_memclr((void *)(uintptr_t)r1_touch_contact_state,100);
 /* Native EABI byte clear returns its advanced pointer. Preserve that word
  * without changing the existing attributable memory provider's void API. */
 return (uintptr_t)r1_touch_contact_state+100u;
}
__attribute__((naked,noinline)) uint32_t r1_touch_synthetic_release_boundary(void)
{__asm__ volatile("push {r2,r3,r4,r5,r6,r7,r8,lr}\nmov r0,sp\nbl synthetic_release_kernel\ncmp r1,#0\nbeq 1f\npop {r2,r3,r4,r5,r6,r7,r8,lr}\nb contact_clear_result\n1: pop {r2,r3,r4,r5,r6,r7,r8,pc}");}
