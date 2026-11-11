/* Native 0x51108 ten-sample trimmed/calibrated pair reduction.
 * Ordinary C storage replaces the incidental register/private-frame contract. */
#include <stdint.h>
#include "../board/native_battery_memory.h"
extern void r1_gxt310_bus_acquire(void),r1_gxt310_bus_release(void);
extern uint32_t r1_gxt310_enable_pair_native(void);
extern void r1_gxt310_disable_pair_native(void);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_gxt310_temperature_channel0(void),r1_gxt310_temperature_channel2(void);
extern uint32_t r1_temperature_calibration_read(void *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_6(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_temp_reduce_ring[] __attribute__((section(".r1.temp.reduce.ring")))="[RING][TEMP] result: temp0=%d, temp2=%d, min0=%d, max0=%d, min2=%d, max2=%d";
const char r1_temp_reduce_sdk[] __attribute__((section(".r1.temp.reduce.sdk")))="[TEMP] result: temp0=%d, temp2=%d, min0=%d, max0=%d, min2=%d, max2=%d";
void r1_temperature_pair_reduce(volatile void *out)
{
 uint32_t maximum2=0xffff0000u,minimum2=65535,value2,value0,maximum0=0xffff0000u,minimum0=65535,sum0=0,sum2=0;
 volatile uint8_t calibration[8]={0};
 volatile uint8_t *output=out;
 r1_gxt310_bus_acquire();
 (void)r1_gxt310_enable_pair_native();
 (void)osDelay(80);
 value0=0;
 do {
  value2=r1_gxt310_temperature_channel0();
  uint32_t value=r1_gxt310_temperature_channel2();
  sum0+=value2;sum2+=value;
  if((int32_t)value2<(int32_t)minimum0)minimum0=value2;
  if((int32_t)value2>(int32_t)maximum0)maximum0=value2;
  if((int32_t)value<(int32_t)minimum2)minimum2=value;
  if((int32_t)value>(int32_t)maximum2)maximum2=value;
  (void)osDelay(5);
  value0=(uint8_t)(value0+1);
 }while(value0<10);
 r1_gxt310_disable_pair_native();
 r1_gxt310_bus_release();
 (void)r1_temperature_calibration_read((void *)(uintptr_t)calibration);
 value0=(uint32_t)(int32_t)(int16_t)((int32_t)(sum0-minimum0-maximum0)/8);
 value2=(uint32_t)(int32_t)(int16_t)((int32_t)(sum2-minimum2-maximum2)/8);
 write16(output+1,value0);write16(output+3,value2);
 for(uint32_t i=0;i<6;++i){
  if(calibration[i]==255)continue;
  int32_t offset0=(int16_t)read16(calibration+1),offset2=(int16_t)read16(calibration+4);
  uint8_t mode=calibration[0];
  if(mode==0)value0=(uint32_t)(int32_t)(int16_t)((int32_t)value0-offset0);
  else if(mode==1)value0=(uint32_t)(int32_t)(int16_t)((int32_t)value0+offset0);
  write16(output+1,value0);
  mode=calibration[3];
  if(mode==0)value2=(uint32_t)(int32_t)(int16_t)((int32_t)value2-offset2);
  else if(mode==1)value2=(uint32_t)(int32_t)(int16_t)((int32_t)value2+offset2);
  write16(output+3,value2);break;
 }
 output[0]=2;
 
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  r1_structured_log_format(0x0d800000,r1_temp_reduce_ring,r1_temp_reduce_ring,value0,value2,minimum0,maximum0,minimum2,maximum2);
 }
 
 if(r1_structured_log_mode_get()&2u){
  nrf_log_frontend_std_6(0x001c0003,r1_temp_reduce_sdk,value0,value2,minimum0,maximum0,minimum2,maximum2);
 }
 
}

