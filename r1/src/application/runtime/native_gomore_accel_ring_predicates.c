#include "native_gomore_accel_ring_predicates.h"
static int32_t half(uint32_t at){return *(volatile int16_t *)(uintptr_t)at;}
static void put_half(uint32_t at,uint32_t x){*(volatile uint16_t *)(uintptr_t)at=(uint16_t)x;}
static uint32_t index(uint32_t cursor,uint32_t step,uint32_t length)
{
 uint32_t position=cursor-step;
 if((int32_t)position<0)position+=length;
 return (uint32_t)(int32_t)(int8_t)position;
}
static uint32_t divide(uint32_t value,uint32_t count)
{
 if(value==0x80000000u && count==0xffffffffu)return value;
 return (uint32_t)((int32_t)value/(int32_t)count);
}
uint32_t r1_gomore_accel_band_count_native(uint32_t input,uint32_t length,uint32_t cursor,uint32_t window,
                                          uint32_t lower,uint32_t upper,uint32_t mode,uint32_t required)
{
 uint32_t hits=0;
 for(uint32_t i=1;(int32_t)i<=(int32_t)window;i++) {
  int32_t x=half(input+index(cursor,i,length)*2u);
  if((int32_t)lower<x && x<(int32_t)upper)hits++;
 }
 if(mode==62u)return (int32_t)hits>=(int32_t)required?1u:UINT32_MAX;
 if(mode==60u && (int32_t)hits<(int32_t)required)return 1;
 return UINT32_MAX;
}
uint32_t r1_gomore_accel_recent_mean3_native(uint32_t x,uint32_t y,uint32_t z,uint32_t length,
                                            volatile uint32_t cursor,uint32_t window,
                                            uint32_t out_x,uint32_t out_y,uint32_t out_z)
{
 /* Capture these incoming stack words before any aliased output clear. */
 volatile struct {uint32_t x,y,z,n;} cached;
 cached.n=window;cached.x=out_x;cached.y=out_y;cached.z=out_z;
 uint32_t n=cached.n;
 put_half(cached.x,0);put_half(cached.y,0);put_half(cached.z,0);
 if((int32_t)(length-n)<0)return x;
 uint32_t a=0,b=0,c=0;
 for(uint32_t i=1;(int32_t)i<=(int32_t)n;i++) {
  uint32_t offset=index(cursor,i,length)*2u;
  a+=(uint32_t)half(x+offset);b+=(uint32_t)half(y+offset);c+=(uint32_t)half(z+offset);
 }
 uint32_t first=n?divide(a,n):0;put_half(cached.x,first);
 uint32_t second=n?divide(b,n):0;put_half(cached.y,second);
 uint32_t third=n?divide(c,n):0;put_half(cached.z,third);
 return third;
}
uint32_t r1_gomore_accel_activity_gate_native(uint32_t ranges,uint32_t x,uint32_t y,uint32_t z,
                                             uint32_t length,uint32_t cursor,uint32_t window)
{
 if((int32_t)(length-window)<0)return UINT32_MAX;
 uint32_t a=0,b=0;
 for(uint32_t i=1;(int32_t)i<=(int32_t)window;i++) {
  uint32_t offset=index(cursor,i,length)*2u;
  /* The native load order is x, y, z, then range. */
  int32_t vx=half(x+offset),vy=half(y+offset),vz=half(z+offset),range=half(ranges+offset);
  if(range>200)a=(uint32_t)(int32_t)(int8_t)(a+1u);
  if(vx+vy+vz>180)b=(uint32_t)(int32_t)(int8_t)(b+1u);
 }
 return (int32_t)a>=3 && (int32_t)b>=3?1u:UINT32_MAX;
}
uint32_t r1_gomore_accel_recent_decision_native(uint32_t state,uint32_t value)
{
 for(uint32_t i=0;i<4;i++)put_half(state+612u+i*2u,(uint32_t)half(state+612u+(i+1u)*2u));
 put_half(state+620u,value);
 /* Stock performs all five reads even though their values are discarded. */
 for(uint32_t i=0;i<5;i++)(void)half(state+612u+i*2u);
 if((int32_t)value>0)return 1;
 if((int32_t)value>-500 && half(state+618u)>-1800 && half(state+616u)>-1200 &&
    half(state+614u)>1000 && half(state+612u)>1000)return 1;
 return UINT32_MAX;
}
