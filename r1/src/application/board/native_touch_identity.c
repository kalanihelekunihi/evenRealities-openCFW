/* Stock 0x5128c resets the ready/output lines, polls the input byte, then
 * reads register zero and returns the low byte independently of bus status. */
#include <stdint.h>
#include "native_touch_transport.h"
#include "native_touch_ready_state.h"
#include "native_battery_memory.h"
extern void r1_touch_bus_acquire_on(void);
extern uint32_t r1_touch_device_op_stop(void),r1_touch_device_op_lock1(void);
extern uint32_t r1_touch_device_op_unlock(void),r1_touch_record_op_0c(void);
extern uint32_t r1_touch_record_op_08(void),r1_touch_power_on_step(void);
extern int32_t osDelay(uint32_t);
__attribute__((noinline)) uint32_t r1_touch_chip_id_probe(void)
{
 int32_t counter=100;
 volatile uint32_t word=0;
 r1_touch_bus_acquire_on();
 (void)osDelay(20);
 (void)r1_touch_device_op_stop();
 (void)r1_touch_device_op_lock1();
 (void)r1_touch_device_op_unlock();
 (void)osDelay(130);
 (void)r1_touch_device_op_lock1();
 (void)osDelay(10);
 (void)r1_touch_record_op_0c();
 (void)osDelay(20);
 (void)r1_stock_dispatch_08(r1_touch_input_device);
 (void)osDelay(40);
 --counter;
 while(counter>=0){
  uint32_t level=r1_touch_ready_level_read();
  if(level==0)break;
  (void)osDelay(2);
  --counter;
 }
 (void)r1_touch_record_op_08();
 (void)r1_touch_request_read_native(0,(void *)(uintptr_t)&word,2);
 (void)osDelay(10);
 (void)r1_touch_device_op_stop();
 (void)r1_touch_power_on_step();
 return (uint8_t)read16((const volatile uint8_t *)&word);
}
