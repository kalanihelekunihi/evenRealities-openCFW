#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"
extern void __aeabi_memclr(void *,size_t);
extern volatile uint8_t *r1_activity_daily_cache_accessor(void);
extern volatile uint8_t *r1_hr_daily_cache_accessor(void);
extern volatile uint8_t *r1_spo2_daily_cache_accessor(void);
extern volatile uint8_t *r1_hrv_daily_cache_accessor(void);
extern uint32_t r1_hr_hour_query(uint32_t,uint32_t,volatile uint32_t *,volatile uint16_t *);
/* Native5a324 plus shared tail3f47c. Provider state and private frame history
 * remain separate gates. The two query output pointers retain native offsets. */
__attribute__((used,noinline)) uint32_t r1_crash_snapshot_body(volatile uint8_t *out,uint32_t timestamp,uint32_t offset,volatile uint32_t *frame)
{
 __aeabi_memclr((void *)(uintptr_t)out,52);
 int32_t minutes=(int16_t)offset;
 if(minutes>720)minutes=720;
 if(minutes< -720)minutes= -720;
 uint32_t adjusted=timestamp+(uint32_t)(minutes*60);
 uint32_t hour=(adjusted%86400u)/3600u;
 out[44]=(uint8_t)hour;
 volatile uint8_t *cache=r1_activity_daily_cache_accessor();
 if(cache){
  uint32_t first=((hour*3u)&127u)*2u;
  for(uint32_t i=0;i<6;i++){
   volatile uint8_t *at=out+16+i*4;
   volatile uint8_t *entry=cache+(first+i)*4;
   write16(at,(read16(at)&0xf000u)|(read16(entry)&0xfffu));
   uint32_t value=read32(entry);
   write16(at+1,(read16(at+1)&0xc00fu)|(((value>>12)&0x3ffu)<<4));
   value=read32(entry);
   write16(at+2,(read16(at+2)&0x3fu)|((value>>22)<<6));
  }
  out[45]|=8;
 }
 cache=r1_hr_daily_cache_accessor();
 if(cache){
  uint32_t count=cache[75];
  if(count){out[49]=(uint8_t)count;write32(out,read32(cache+76));out[45]|=1;}
  uint32_t at=hour*3;
  if(cache[at]){
   out[46]=cache[at];out[47]=cache[at+1];out[48]=cache[at+2];
   frame[0]=0;*(volatile uint16_t *)(frame+1)=0;
   (void)r1_hr_hour_query(0,hour,frame,(volatile uint16_t *)(frame+1));
   write32(out+4,frame[0]);write16(out+40,*(volatile uint16_t *)(frame+1));out[45]|=1;
  }
 }
 cache=r1_spo2_daily_cache_accessor();
 if(cache){uint32_t count=cache[75];if(count){out[50]=(uint8_t)count;write32(out+8,read32(cache+76));out[45]|=2;}}
 cache=r1_hrv_daily_cache_accessor();
 if(!cache)return 0;
 uint32_t count=read16(cache+147);
 if(!count)return (uint32_t)(uintptr_t)cache;
 write16(out+42,count);write32(out+12,read32(cache+149));
 uint32_t flags=out[45]|4u;out[45]=(uint8_t)flags;return flags;
}
__attribute__((naked)) uint32_t r1_health_crash_snapshot_builder(void *out __attribute__((unused)),uint32_t timestamp __attribute__((unused)),uint32_t offset __attribute__((unused)))
{
 __asm__ volatile("push {r2,r3,r4,r5,r6,lr}\n"
                  "mov r3,sp\n"
                  "bl r1_crash_snapshot_body\n"
                  "pop {r2,r3,r4,r5,r6,pc}\n");
}
