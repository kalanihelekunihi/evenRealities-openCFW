#include <stdint.h>
#include "../board/native_battery_memory.h"
extern volatile uint8_t r1_touch_contact_state[100];
extern volatile uint8_t r1_touch_release_timer_pending,r1_touch_synthetic_flag;
extern volatile uint32_t r1_touch_client_bits;
extern void *volatile r1_low_battery_thread_handle;
extern void r1_touch_release_timer_callback(uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_0(uint32_t,const char *);
extern uint32_t r1_reset_trace_reboot_caller_write(uint32_t),osThreadFlagsSet(void *,uint32_t);
extern uint32_t osKernelGetTickCount(void),r1_advertising_configuration_byte_get(void),r1_glasses_connection_handle_get(void);
extern uint32_t r1_ble_tx_queue_dispatch_type0(uint32_t,const void *,uint32_t);
/* Remaining fields of the service context. Existing byte/client owners alias
 * offsets0/2/20; eventual whole-context ownership must preserve these cells. */
volatile uint8_t r1_touch_last_direction __attribute__((section(".r1.touch.gesture.direction")))=0;
volatile uint16_t r1_touch_direction_count __attribute__((section(".r1.touch.gesture.count"),aligned(2)))=0;
volatile uint32_t r1_touch_direction_time __attribute__((section(".r1.touch.gesture.time"),aligned(4)))=0;
volatile uint32_t r1_touch_up_log_time __attribute__((section(".r1.touch.gesture.up_time"),aligned(4)))=0;
volatile uint32_t r1_touch_down_log_time __attribute__((section(".r1.touch.gesture.down_time"),aligned(4)))=0;
const char r1_gesture_reset_ring[] __attribute__((section(".r1.touch.gesture.reset_ring")))="[RING]touch five click, reset host";
const char r1_gesture_reset_sdk[] __attribute__((section(".r1.touch.gesture.reset_sdk")))="touch five click, reset host";
const char r1_gesture_single_ring[] __attribute__((section(".r1.touch.gesture.single_ring")))="[RING]======================================== SINGLE_CLICK ========================================";
const char r1_gesture_single_sdk[] __attribute__((section(".r1.touch.gesture.single_sdk")))="======================================== SINGLE_CLICK ========================================";
const char r1_gesture_double_ring[] __attribute__((section(".r1.touch.gesture.double_ring")))="[RING]======================================== DOUBLE_CLICK ========================================";
const char r1_gesture_double_sdk[] __attribute__((section(".r1.touch.gesture.double_sdk")))="======================================== DOUBLE_CLICK ========================================";
const char r1_gesture_long_ring[] __attribute__((section(".r1.touch.gesture.long_ring")))="[RING]======================================== LONG_PRESS ========================================";
const char r1_gesture_long_sdk[] __attribute__((section(".r1.touch.gesture.long_sdk")))="======================================== LONG_PRESS ========================================";
const char r1_gesture_up_ring[] __attribute__((section(".r1.touch.gesture.up_ring")))="[RING]======================================== SLIDER_UP ========================================";
const char r1_gesture_up_sdk[] __attribute__((section(".r1.touch.gesture.up_sdk")))="======================================== SLIDER_UP ========================================";
const char r1_gesture_down_ring[] __attribute__((section(".r1.touch.gesture.down_ring")))="[RING]======================================== SLIDER_DOWN ========================================";
const char r1_gesture_down_sdk[] __attribute__((section(".r1.touch.gesture.down_sdk")))="======================================== SLIDER_DOWN ========================================";
const char r1_gesture_release_ring[] __attribute__((section(".r1.touch.gesture.release_ring")))="[RING]============================================ LONG_RELEASE ========================================";
const char r1_gesture_release_sdk[] __attribute__((section(".r1.touch.gesture.release_sdk")))="============================================ LONG_RELEASE ========================================";
static void gesture_log(const char *ring,const char *sdk)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c000000,ring,ring);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_0(0x001c0003,sdk);
}
__attribute__((used,noinline)) static uint32_t gesture_kernel(const volatile uint8_t *record,volatile uint8_t *frame)
{
 uint32_t initial=record[0];if(!initial)return 0;
 uint32_t request_reset=record[3],now=read32(r1_touch_contact_state+40);
 uint32_t direction=(initial&32u)?1u:(initial&64u)?2u:0u;
 if((initial&30u)||(direction && (uint32_t)(now-r1_touch_direction_time)>400u)){
  r1_touch_last_direction=0;r1_touch_direction_count=0;
 }
 if((*(const volatile uint8_t *)&r1_touch_client_bits&2u)&&request_reset){
  gesture_log(r1_gesture_reset_ring,r1_gesture_reset_sdk);
  (void)r1_reset_trace_reboot_caller_write(2);
  (void)osThreadFlagsSet(r1_low_battery_thread_handle,2);
 }
 if(direction){
  uint32_t previous=r1_touch_last_direction;
  if(previous && previous!=direction && r1_touch_direction_count>=2){
   r1_touch_last_direction=(uint8_t)direction;r1_touch_direction_count=1;r1_touch_direction_time=now;
   return (uintptr_t)&r1_touch_release_timer_pending;
  }
  r1_touch_direction_count=previous==direction?(uint16_t)(r1_touch_direction_count+1u):1;
  r1_touch_last_direction=(uint8_t)direction;r1_touch_direction_time=now;
 }
 if((record[0]&2u)&&r1_touch_contact_state[48]&&!r1_touch_release_timer_pending){
  r1_touch_release_timer_pending=1;
  r1_native_delayed_schedule(r1_touch_release_timer_callback,0,307);
 }
 uint32_t event=record[0],kind;
 if(event&4u){gesture_log(r1_gesture_single_ring,r1_gesture_single_sdk);kind=1;}
 else if(event&8u){gesture_log(r1_gesture_double_ring,r1_gesture_double_sdk);kind=2;}
 else if(event&16u){gesture_log(r1_gesture_long_ring,r1_gesture_long_sdk);kind=0;}
 else if(event&32u){
  if((uint32_t)(now-r1_touch_up_log_time)>1000u){r1_touch_up_log_time=now;gesture_log(r1_gesture_up_ring,r1_gesture_up_sdk);}kind=4;
 }else if(event&64u){
  if((uint32_t)(now-r1_touch_down_log_time)>1000u){r1_touch_down_log_time=now;gesture_log(r1_gesture_down_ring,r1_gesture_down_sdk);}kind=5;
 }else{
  if(!(event&2u))return event<<30;
  if(!r1_touch_synthetic_flag)return 0;
  gesture_log(r1_gesture_release_ring,r1_gesture_release_sdk);kind=8;
 }
 uint32_t distance=record[1],velocity=record[2],tick=osKernelGetTickCount();
 write32(frame,0);write32(frame+4,0);frame[2]=97;frame[4]=(uint8_t)kind;frame[1]=9;frame[5]=(uint8_t)distance;
 write32(frame+8,0);frame[3]=0;frame[6]=(uint8_t)velocity;write32(frame+7,tick);
 uint32_t size=r1_advertising_configuration_byte_get()==85?5u:11u;
 uint32_t handle=r1_glasses_connection_handle_get();if(handle==0xffffu)return handle;
 handle=r1_glasses_connection_handle_get();
 return r1_ble_tx_queue_dispatch_type0(handle,(const void *)(uintptr_t)frame,size);
}
/* Native frame stores packet bytes over saved r1/r2/r3 and restores their
 * actual contents. The C kernel's private footprint remains separately gated. */
__attribute__((naked,noinline)) uint32_t r1_touch_gesture_dispatch_boundary(const void *record __attribute__((unused)))
{__asm__ volatile("push {r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,lr}\nmov r1,sp\nbl gesture_kernel\npop {r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,pc}");}
