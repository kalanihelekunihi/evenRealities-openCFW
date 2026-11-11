/* Stock R1 sector selection 0x8fe28 and erase fallback 0x8fc6c. */
#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_sleep_sync_context_prefix[3];
extern uint32_t r1_sleep_sector_count(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
static uint32_t ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static uint32_t offset(uint32_t index)
{
 volatile uint32_t *context=r1_sleep_sync_context_prefix;
 const volatile uint8_t *partition=(const volatile uint8_t *)(uintptr_t)context[1];
 return read32(partition+52)+(index<<12);
}
static void read_header(uint32_t index,uint32_t *header)
{
 volatile uint32_t *context=r1_sleep_sync_context_prefix;
 const volatile uint8_t *partition=(const volatile uint8_t *)(uintptr_t)context[1];
 const volatile uint8_t *device=(const volatile uint8_t *)(uintptr_t)context[2];
 uint32_t address=read32(partition+52)+(index<<12);
 int (*read)(long,void *,size_t)=(void *)(uintptr_t)read32(device+40);
 (void)read((long)address,header,16);
}
uint32_t r1_sleep_sector_select(void)
{
 uint32_t count=r1_sleep_sector_count();
 uint32_t header[4]={0,0,0,0};
 for(uint32_t index=0;index<count;index++){
  read_header(index,header);
  if(header[0]==UINT32_MAX ||
     (header[1]==UINT32_MAX && header[2]==UINT32_MAX) ||
     (header[0]==UINT32_C(0xccffaabb) && header[1]!=UINT32_C(0x66889977)))
   return (uint32_t)(int32_t)(int8_t)index;
 }
 return UINT32_MAX;
}
uint32_t r1_sleep_sector_fallback(void)
{
 uint32_t count=r1_sleep_sector_count();
 uint32_t header[4]={0,0,0,0};
 uint32_t minimum=UINT32_MAX,index=UINT32_MAX;
 for(uint32_t candidate=0;candidate<count;candidate++){
  read_header(candidate,header);
  if(header[2]<minimum){minimum=header[2];index=(uint32_t)(int32_t)(int8_t)candidate;}
 }
 if(index==UINT32_MAX)index=0;
 index=(uint8_t)index;
 /* This second query is live. Even a zero-count store reaches sector0 erase. */
 if(r1_sleep_sector_count()<=index){
  const char *ring="[RING]sleep storage erase sector out of range";
  if(ring_enabled())(void)r1_structured_log_format(0x04000000u,ring,ring);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001u,"sleep storage erase sector out of range");
  index=0;
 }
 volatile uint32_t *context=r1_sleep_sync_context_prefix;
 const volatile uint8_t *partition=(const volatile uint8_t *)(uintptr_t)context[1];
 const volatile uint8_t *device=(const volatile uint8_t *)(uintptr_t)context[2];
 uint32_t address=read32(partition+52)+(index<<12);
 int (*erase)(long,size_t)=(void *)(uintptr_t)read32(device+48);
 (void)erase((long)address,4096);
 const char *ring="[RING]sleep storage erase offset: %08X";
 if(ring_enabled())(void)r1_structured_log_format(0x0c400000u,ring,ring,offset(index));
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003u,"sleep storage erase offset: %08X",offset(index));
 return (uint32_t)(int32_t)(int8_t)index;
}
