#include "native_gomore_accel_collect.h"
#include "native_gomore_i16_statistics.h"
#include "native_float_to_signed.h"
static uint32_t byte(uint32_t at){return *(volatile uint8_t *)(uintptr_t)at;}
static void slot(uint32_t state,uint32_t offset,uint32_t value)
{*(volatile uint16_t *)(uintptr_t)(state+offset+byte(state+0x52u)*2u)=(uint16_t)value;}
uint32_t r1_gomore_accel_collect_native(uint32_t state,uint32_t x,uint32_t y,uint32_t z,
                                       volatile uint32_t fourth,uint32_t count)
{
 volatile struct {uint32_t state,x,y,z;} frame;
 frame.state=state;frame.x=x;frame.y=y;frame.z=z;
 uint32_t mx=r1_gomore_i16_mean_native(x,count);
 uint32_t my=r1_gomore_i16_mean_native(y,count);
 uint32_t mz=r1_gomore_i16_mean_native(frame.z,count);
 uint32_t ma=r1_gomore_i16_mean_native(fourth,count);
 slot(state,0x1e4,mx);slot(state,0x1f4,my);slot(state,0x12,mz);
 uint32_t result=r1_native_float_to_signed32(r1_gomore_i16_deviation_native(x,count,mx));
 slot(state,2,result);
 result=r1_native_float_to_signed32(r1_gomore_i16_deviation_native(y,count,my));slot(state,0x204,result);
 result=r1_native_float_to_signed32(r1_gomore_i16_deviation_native(frame.z,count,mz));slot(state,0x214,result);
 slot(state,0x32,ma);
 result=r1_native_float_to_signed32(r1_gomore_i16_deviation_native(fourth,count,ma));slot(state,0x22,result);
 result=r1_gomore_i16_range_native(fourth,count);slot(state,0x42,result);
 uint32_t short_count=(uint32_t)(int32_t)(int8_t)count;
 result=r1_gomore_i16_mean_difference_native(fourth,short_count);slot(state,0x224,result);
 result=r1_gomore_i16_mean_difference_native(x,short_count);slot(state,0x234,result);
 result=r1_gomore_i16_mean_difference_native(y,short_count);slot(state,0x244,result);
 result=r1_gomore_i16_mean_difference_native(frame.z,short_count);slot(state,0x254,result);
 uint32_t next=byte(state+0x52u)+1u;
 *(volatile uint8_t *)(uintptr_t)(state+0x52u)=(uint8_t)(next<8u?next:0u);
 return 0;
}
