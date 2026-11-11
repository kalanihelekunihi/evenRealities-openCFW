/* Stock R1 0x901e4: write a sector completion marker after scanning counters. */
#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_sleep_sync_context_prefix[3];
extern uint32_t r1_sleep_sector_count(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
uint32_t r1_sleep_sector_finalize(uint32_t sector)
{
 volatile uint32_t *context=r1_sleep_sync_context_prefix;
 const volatile uint8_t *partition=(const volatile uint8_t *)(uintptr_t)context[1];
 /* The target address precedes the count query and remains fixed thereafter. */
 uint32_t target=read32(partition+52)+(sector<<12);
 uint32_t marker[4]={UINT32_C(0xccffaabb),UINT32_C(0x66889977),0,0};
 uint32_t count=r1_sleep_sector_count();
 uint32_t header[4]={0,0,0,0};
 uint32_t minimum=UINT32_MAX;
 for(uint32_t index=0;index<count;index++){
  partition=(const volatile uint8_t *)(uintptr_t)context[1];
  const volatile uint8_t *device=(const volatile uint8_t *)(uintptr_t)context[2];
  int (*read)(long,void *,size_t)=(void *)(uintptr_t)read32(device+40);
  (void)read((long)(read32(partition+52)+(index<<12)),header,sizeof(header));
  if(header[2]<minimum)minimum=header[2];
 }
 marker[2]=(minimum==UINT32_MAX?0:minimum)+1;
 const char *ring="[RING]sleep storage write full count: %d";
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000u,ring,ring,marker[2]);
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_1(0x001c0003u,"sleep storage write full count: %d",marker[2]);
 const volatile uint8_t *device=(const volatile uint8_t *)(uintptr_t)context[2];
 int (*write)(long,const void *,size_t)=(void *)(uintptr_t)read32(device+44);
 return write((long)target,marker,sizeof(marker))==0;
}
