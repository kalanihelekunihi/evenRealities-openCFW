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
/* Stock 0x934e4 clears every byte of this 44-byte message before enqueueing.
 * The message provider consumes it synchronously under the queue-copy API. */
void r1_touch_release_timer_callback(uint32_t argument)
{
 (void)argument;
 uint32_t message[11];
 __aeabi_memclr(message,sizeof message);
 message[1]=5;
 message[2]=0;
 (void)r1_touch_task_message_boundary(message);
}
/* Internal result: the high word requests contact clearing; the low word
 * carries the native inactive return byte. Each emitted four-byte record is
 * assigned in full before the gesture consumer reads it. */
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
/* Ordinary C ABI: private stack addresses and caller-clobbered register
 * restoration are not part of the message/gesture contract. */
uint32_t r1_touch_synthetic_release_boundary(void)
{
 uint32_t records[2];
 uint64_t result=synthetic_release_kernel(records);
 return result>>32 ? contact_clear_result() : (uint32_t)result;
}

/* Stock 0x8e9d0 shares contact storage with release and gesture consumers. */
void r1_touch_pending_tap_timeout(void)
{
 if(r1_touch_contact_state[48]) {
  r1_touch_contact_state[48]=0;
  r1_touch_contact_state[0]=0;
  uint8_t record[4]={4,0,r1_touch_contact_state[95],0};
  (void)r1_touch_gesture_dispatch_boundary(record);
 }
 r1_touch_release_timer_pending=0;
}
