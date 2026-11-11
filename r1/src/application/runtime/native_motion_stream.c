#include <stdint.h>
#include "native_motion_operations.h"
#include "../board/native_battery_memory.h"
/* Only these authenticated cold cells are owned, not the surrounding motion
 * selection/configuration records or licensed sensor provider bodies. */
volatile uint32_t r1_motion_selected_provider __attribute__((section(".r1.motion.selected"),aligned(4)))=0;
volatile uint8_t r1_motion_calibration_bypass __attribute__((section(".r1.motion.calib.bypass"),aligned(1)))=0;
extern uint32_t r1_motion_probe_and_select_provider(void);
extern void *volatile r1_device_info_kv_handle;
extern uint32_t r1_kv_class_read(void *,void *,uint32_t),r1_stream_tick_now(void);
uint32_t r1_motion_selected_provider_initialize(void)
{
 uint32_t address = r1_motion_selected_provider;
 if (address == 0) {
  (void)r1_motion_probe_and_select_provider();
  address = r1_motion_selected_provider;
 }
 if (address != 0) {
  const volatile r1_motion_table *selected =
   (const volatile r1_motion_table *)(uintptr_t)address;
  uint32_t (*configure)(void) = selected->configure;
  if (configure != 0)
   return configure();
 }
 return 0;
}
uint32_t r1_motion_initialize_entry(uint32_t context __attribute__((unused)))
{
 return r1_motion_selected_provider_initialize();
}
uint32_t r1_motion_stream_close_boundary(uint32_t context __attribute__((unused))){return 1;}
/* Interrupt entries use a notification-only C ABI; sensor-task callers do
 * not consume the stock incidental R0 or provider release status. */
void r1_native_motion_interrupt(void)
{
 const volatile r1_motion_table *selected =
  (const volatile r1_motion_table *)(uintptr_t)r1_motion_selected_provider;
 if (selected == 0)
  return;
 void (*event)(void) = selected->interrupt.notify;
 if (event != 0)
  event();
}
int32_t r1_motion_selected_fifo_read(uint8_t *destination, uint32_t samples)
{
 const volatile r1_motion_table *selected =
  (const volatile r1_motion_table *)(uintptr_t)r1_motion_selected_provider;
 if (selected != 0) {
  int32_t (*fifo)(uint8_t *, uint32_t) = selected->fifo;
  if (fifo != 0)
   return fifo(destination, samples);
 }
 return -1;
}
__attribute__((noinline)) uint32_t r1_motion_calibration_bypassed(void){return r1_motion_calibration_bypass;}
__attribute__((used,noinline)) uint32_t r1_motion_calibration_body(volatile uint8_t *out,volatile uint8_t *scratch)
{
 (void)r1_kv_class_read(r1_device_info_kv_handle,(void *)(uintptr_t)scratch,124);
 write32(out,read32(scratch+68));uint32_t last=read16(scratch+72);write16(out+4,last);return last;
}
/* Same valid 124-byte cached-class precondition as the temperature reader. */
__attribute__((noinline)) uint32_t r1_motion_calibration_read(volatile void *out)
{
 _Alignas(4) volatile uint8_t record[124];
 return r1_motion_calibration_body(out,record);
}
/* Packed may-alias views preserve the native unaligned halfword accesses. */
struct __attribute__((packed, may_alias)) r1_motion_halfword { uint16_t value; };
static uint16_t r1_motion_load_half(const volatile uint8_t *p)
{ return ((const volatile struct r1_motion_halfword *)p)->value; }
static void r1_motion_store_half(volatile uint8_t *p, uint32_t value)
{ ((volatile struct r1_motion_halfword *)p)->value = (uint16_t)value; }
__attribute__((used,noinline)) void r1_motion_adjust_samples(volatile uint8_t *destination,uint32_t count,volatile uint8_t *offset)
{
 if(r1_motion_load_half(offset)==65535 && r1_motion_load_half(offset+2)==65535 && r1_motion_load_half(offset+4)==65535){r1_motion_store_half(offset,0);r1_motion_store_half(offset+2,0);r1_motion_store_half(offset+4,0);}
 for(uint32_t i=0;i<count;i++)if(!r1_motion_calibration_bypassed()){
  volatile uint8_t *sample=destination+i*6;
  uint32_t delta=r1_motion_load_half(offset);uint32_t value=r1_motion_load_half(sample);r1_motion_store_half(sample,value+delta);
  delta=r1_motion_load_half(offset+2);value=r1_motion_load_half(sample+2);r1_motion_store_half(sample+2,value+delta);
  value=r1_motion_load_half(sample+4);delta=r1_motion_load_half(offset+4);r1_motion_store_half(sample+4,value+delta);
 }
}
struct __attribute__((packed)) r1_motion_batch {
 uint8_t samples[180];
 uint16_t count;
 uint8_t reserved[2];
 uint32_t timestamp;
};
_Static_assert(sizeof(struct r1_motion_batch)==188 &&
               offsetof(struct r1_motion_batch,count)==180 &&
               offsetof(struct r1_motion_batch,timestamp)==184,
               "native motion batch layout");
uint32_t r1_motion_thirty_sample_batch_producer(uint8_t *destination,
 uint32_t length, uint32_t context __attribute__((unused)))
{
 if (destination == 0 || length != 188)
  return 0;
 int32_t result = r1_motion_selected_fifo_read(destination, 30);
 if (result < 0)
  return 0;
 uint8_t offset[8] = {0};
 (void)r1_motion_calibration_read(offset);
 uint16_t count = (uint16_t)result;
 r1_motion_adjust_samples(destination, count, offset);
 volatile struct r1_motion_batch *batch =
  (volatile struct r1_motion_batch *)destination;
 batch->count = count;
 batch->timestamp = r1_stream_tick_now();
 return 188;
}
