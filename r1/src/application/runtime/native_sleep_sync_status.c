/* Stock R1 0x5b6f4: match acknowledged headers and program the sync marker. */
#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_sleep_sync_context_prefix[3];
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
static uint32_t enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
void r1_sleep_sync_status_backend(const volatile uint8_t *rows,uint32_t length)
{
 if(!rows || !length){
  const char *ring="[RING]sync status buffer is null";
  if(enabled())(void)r1_structured_log_format(0x04000000u,ring,ring);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001u,"sync status buffer is null");
  return;
 }
 uint32_t count=(uint8_t)(length/12u);
 uint32_t header[6];__aeabi_memclr(header,sizeof(header));
 uint32_t marker=UINT32_C(0x11223344);
 volatile uint32_t *context=r1_sleep_sync_context_prefix;
 for(uint32_t index=0;index<count;index++){
  const volatile uint8_t *row=rows+index*12;
  const volatile uint8_t *device=(const volatile uint8_t *)(uintptr_t)context[2];
  uint32_t address=read32(row);
  int (*read)(long,void *,size_t)=(void *)(uintptr_t)read32(device+40);
  (void)read((long)address,header,sizeof(header));
  if(header[2]!=read32(row+4) || header[3]!=read32(row+8))continue;
  device=(const volatile uint8_t *)(uintptr_t)context[2];
  int (*write)(long,const void *,size_t)=(void *)(uintptr_t)read32(device+44);
  if(write((long)(address+20u),&marker,sizeof(marker))!=0){
   const char *ring="[RING]sleep storage write synchronize to head fail:%d";
   if(enabled())(void)r1_structured_log_format(0x04400000u,ring,ring,read32(row));
   if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0001u,"sleep storage write synchronize to head fail:%d",read32(row));
  }
 }
}
#include <stdint.h>
uint32_t r1_sleep_sync_context_prefix[3] __attribute__((section(".r1.sleep.sync.context"),aligned(4)))={0};
