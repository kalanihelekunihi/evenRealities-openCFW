/* Stock 0x46650 touch dispatcher and its queue/recovery/factory adapters. */
#include <stdint.h>
#include "cmsis_os2.h"
#include "../board/native_touch_task_control.h"
#include "../board/native_touch_transport.h"
#include "../board/native_battery_memory.h"
extern void *volatile r1_touch_task_message_queue;
extern volatile uint32_t r1_touch_io_watchdog;
extern volatile uint8_t r1_touch_board_active;
extern uint32_t r1_touch_ready_level_read(void),r1_touch_board_open(void);
extern uintptr_t r1_touch_pending_flag_consume(void);
extern uint32_t r1_touch_record_op_08(void),r1_touch_record_op_0c_b(void);
extern void r1_shared_power_client_acquire(uint32_t),delayed_touch_release(uint32_t);
extern _Noreturn void r1_native_worker_park(uint32_t,uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern uint32_t r1_touch_task_event_post(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
/* Genuine lower dependencies; their bodies are not replaced with stubs. */
extern void r1_iqs7211e_irq_worker(void),r1_touch_pending_tap_timeout(void);
volatile uint8_t r1_touch_task_active __attribute__((section(".r1.touch.task.active"),aligned(1)))=0;
volatile uint8_t r1_touch_slider_flag __attribute__((section(".r1.touch.slider_flag"),aligned(1)))=0;
volatile struct r1_touch_task_parameters r1_touch_parameters
 __attribute__((section(".r1.touch.task.parameters"),aligned(2)))={8,0,240,26,1};
volatile struct r1_touch_factory_parameters r1_touch_factory_state
 __attribute__((section(".r1.touch.factory"),aligned(4)))={0,4,0,4,0,240,1};
#define TEXT(name,value) const char r1_touch_dispatch_##name[]=value
TEXT(close_ring,"[RING]TOUCH_EVENT_CLOSE");TEXT(close_sdk,"TOUCH_EVENT_CLOSE");
TEXT(recovery_ring,"[RING]ATI_ERR_RECOVERY: schedule reinit in 100ms");TEXT(recovery_sdk,"ATI_ERR_RECOVERY: schedule reinit in 100ms");
TEXT(alp_ring,"[RING]TOUCH_EVENT_ALP_ATI_ERROR");TEXT(alp_sdk,"TOUCH_EVENT_ALP_ATI_ERROR");
TEXT(ati_ring,"[RING]TOUCH_EVENT_ATI_ERROR");TEXT(ati_sdk,"TOUCH_EVENT_ATI_ERROR");
TEXT(timer_ring,"[RING]ATI_ERR_RECOVERY: post TOUCH_EVENT_INIT");TEXT(timer_sdk,"ATI_ERR_RECOVERY: post TOUCH_EVENT_INIT");
TEXT(irq_ring,"[RING]bc_touch_button_irq_process flag=false, return\r\n");TEXT(irq_sdk,"bc_touch_button_irq_process flag=false, return\r\n");
static void log_event(uint32_t marker,uint32_t sdk,const char *ring,const char *text)
{
 if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(marker,ring,ring);
 if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(sdk,text);
}
uint32_t r1_touch_slider_flag_get(void) { return r1_touch_slider_flag!=0; }
uint32_t r1_touch_slider_flag_clear(void) { r1_touch_slider_flag=0;return 0; }
void r1_touch_recovery_timer_callback(uint32_t argument)
{
 (void)argument;(void)r1_touch_slider_flag_clear();
 log_event(0x08000000,0x001c0002,r1_touch_dispatch_timer_ring,r1_touch_dispatch_timer_sdk);
 (void)r1_touch_task_event_post(2);
}
void r1_touch_button_irq_process(void)
{
 if (!r1_touch_board_active) {
  log_event(0x0c000000,0x001c0003,r1_touch_dispatch_irq_ring,r1_touch_dispatch_irq_sdk);return;
 }
 if (r1_touch_ready_level_read()!=0) return;
 (void)r1_touch_record_op_08();r1_iqs7211e_irq_worker();(void)r1_touch_record_op_0c_b();
}
void r1_touch_button_irq_thunk(void) { r1_touch_button_irq_process(); }
uint32_t r1_iqs7211e_factory_communication_end(void)
{
 uint8_t zero=0;
 return r1_iqs7211e_register_write_port(0x56,255,&zero,1,1);
}
static uint32_t factory_marker(uint8_t marker)
{
 r1_touch_factory_state.marker=marker;
 (void)r1_touch_record_op_08();(void)r1_iqs7211e_factory_communication_end();
 return r1_touch_record_op_0c_b();
}
uint32_t r1_iqs7211e_factory_marker_1(void) { return factory_marker(1); }
uint32_t r1_iqs7211e_factory_marker_2(void) { return factory_marker(2); }
uint32_t r1_iqs7211e_factory_marker_3(uint32_t value)
{uint32_t result=factory_marker(3);r1_touch_factory_state.first=(uint8_t)value;return result;}
uint32_t r1_iqs7211e_factory_marker_4(uint32_t value)
{uint32_t result=factory_marker(4);r1_touch_factory_state.half=(uint16_t)value;return result;}
uint32_t r1_iqs7211e_factory_marker_5(uint32_t value)
{uint32_t result=factory_marker(5);r1_touch_factory_state.second=(uint8_t)value;return result;}
uint32_t r1_iqs7211e_factory_marker_6(uint32_t value)
{uint32_t result=factory_marker(6);r1_touch_factory_state.word=value;return result;}
void r1_touch_config_queue_consume(void)
{
 uint8_t message[44]={0};
 while (osMessageQueueGet(r1_touch_task_message_queue,message,NULL,0)==0) {
  uint32_t length=read32(message+8);
  switch ((uint8_t)read32(message+4)) {
   case 1:if(length)r1_touch_parameters.first=message[12];break;
   case 2:if(length>=2)r1_touch_parameters.second=read16(message+12);break;
   case 3:if(length)r1_touch_parameters.third=message[12];break;
   case 4:if(length)r1_touch_parameters.fourth=message[12];break;
   case 5:r1_touch_pending_tap_timeout();break;
   default:break;
  }
 }
}
void r1_iqs7211e_touch_task_dispatcher(uint32_t flags)
{
 if (flags&0x400000u) r1_touch_config_queue_consume();
 if (flags&1u) r1_touch_button_irq_thunk();
 if (flags&0x800000u) r1_native_worker_park(9,r1_touch_io_watchdog);
 if (flags&2u) {
  if (!r1_touch_task_active) r1_touch_task_active=1;
  r1_shared_power_client_acquire(2);
  r1_native_delayed_schedule(delayed_touch_release,0,0x800);
  (void)osDelay(1);(void)r1_touch_board_open();
 }
 if (flags&4u) {
  log_event(0x0c000000,0x001c0003,r1_touch_dispatch_close_ring,r1_touch_dispatch_close_sdk);
  r1_touch_task_active=0;(void)r1_touch_pending_flag_consume();
  if (r1_touch_slider_flag_get()) {
   log_event(0x08000000,0x001c0002,r1_touch_dispatch_recovery_ring,r1_touch_dispatch_recovery_sdk);
   (void)r1_native_delayed_cancel(r1_touch_recovery_timer_callback,0);
   r1_native_delayed_schedule(r1_touch_recovery_timer_callback,0,0x66);
  }
 }
 if (flags&16u) log_event(0x0c000000,0x001c0003,r1_touch_dispatch_alp_ring,r1_touch_dispatch_alp_sdk);
 if (flags&32u) log_event(0x0c000000,0x001c0003,r1_touch_dispatch_ati_ring,r1_touch_dispatch_ati_sdk);
 if (flags&64u) {(void)r1_iqs7211e_factory_marker_1();return;}
 if (flags&128u) {(void)r1_iqs7211e_factory_marker_2();return;}
 if (flags&256u) {(void)r1_iqs7211e_factory_marker_3(r1_touch_parameters.first);return;}
 if (flags&512u) {(void)r1_iqs7211e_factory_marker_4(r1_touch_parameters.second);return;}
 if (flags&1024u) {(void)r1_iqs7211e_factory_marker_5(r1_touch_parameters.third);return;}
 if (flags&2048u) {(void)r1_iqs7211e_factory_marker_6(r1_touch_parameters.fourth);return;}
}
