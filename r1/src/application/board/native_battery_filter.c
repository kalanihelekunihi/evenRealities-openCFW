/* Stock five-sample battery filter, using ordinary C storage and status ABI. */
#include <stdint.h>
#include "native_battery_context.h"
#include "native_battery_memory.h"
extern uint32_t r1_stock_dispatch_08(uint32_t);
extern uint32_t r1_stock_dispatch_0c(uint32_t);
extern uint32_t r1_stock_dispatch_10(uint32_t,uint32_t,volatile void *,uint32_t);
extern void nrf_delay_ms(uint32_t);
extern uint32_t osDelay(uint32_t);
uint32_t r1_battery_five_sample_filter_and_conversion(void)
{
 volatile struct {uint32_t sample;uint16_t samples[5],padding;} frame={0,{0,0,0,0,0},0};
 _Static_assert(sizeof(frame)==16 && offsetof(__typeof__(frame),samples)==4,"sample workspace layout");
 volatile uint8_t *context=(volatile uint8_t *)&r1_battery_runtime_storage;
 uint32_t sum=0,first=65535,second=65535;
 (void)r1_stock_dispatch_08(read32(context+16));
 for (uint32_t i=0;i<5;++i) {
  (void)r1_stock_dispatch_10(read32(context+16),0,&frame.sample,1);
  uint32_t value=read16((const volatile uint8_t *)&frame.sample);
  frame.samples[i]=(uint16_t)value;sum+=value;
  write16((volatile uint8_t *)&frame.sample,0);
  if (context[1]) (void)osDelay(2);else nrf_delay_ms(2);
 }
 (void)r1_stock_dispatch_0c(read32(context+16));
 for (uint32_t i=0;i<5;++i) {
  uint32_t value=frame.samples[i];
  if (value<first) {second=first;first=value;}else if(value<second) second=value;
 }
 uint32_t average=(uint16_t)((sum-first-second)/3u);
 uint32_t product=average*292u;product*=2989u;
 return (uint16_t)(product/0x79d38u);
}
