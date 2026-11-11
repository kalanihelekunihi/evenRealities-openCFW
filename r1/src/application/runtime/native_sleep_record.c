/* Ordinary C for native sleep record store 0x5b890 and event 0x8dc94. */
#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_sleep_sync_context_prefix[3];
extern uint32_t r1_sleep_sector_select(void),r1_sleep_sector_fallback(void);
extern uint32_t r1_sleep_sector_write(uint32_t,const volatile uint8_t *,uint32_t);
extern void r1_sleep_erase_all(void);
extern void r1_health_event_notification_throttle(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
static uint32_t record_ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void record_error(const char *ring,const char *sdk)
{
 if(record_ring_enabled())(void)r1_structured_log_format(0x04000000u,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001u,sdk);
}
__attribute__((noinline,section(".text.r1_sleep_record_store"))) uint32_t r1_sleep_record_store(const volatile uint8_t *data,uint32_t length)
{
 if(!*(volatile uint8_t *)r1_sleep_sync_context_prefix){
  record_error("[RING]sleep storage not init","sleep storage not init");return 0;
 }
 if(length>3888 || !data){
  record_error("[RING]sleep storage fail, size too large","sleep storage fail, size too large");return 0;
 }
 for(uint32_t attempt=0;attempt<2;attempt++){
  uint32_t selected=r1_sleep_sector_select();
  if(selected==UINT32_MAX)selected=r1_sleep_sector_fallback();
  if(r1_sleep_sector_write((uint8_t)selected,data,length)){
   const char *ring="[RING]sleep storage writable sector: %d";
   if(record_ring_enabled())(void)r1_structured_log_format(0x0c400000u,ring,ring,selected);
   if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003u,"sleep storage writable sector: %d",selected);
   return 1;
  }
 }
 r1_sleep_erase_all();
 record_error("[RING]sleep storage write data fail, flash reset","sleep storage write data fail, flash reset");return 0;
}
__attribute__((section(".text.r1_event_service_0008dc94"))) void r1_event_service_0008dc94(const volatile uint8_t *data)
{
 if(!data){record_error("[RING]sleep data is null","sleep data is null");return;}
 uint32_t length=(uint16_t)(read16(data+30)+32u);
 if(r1_sleep_record_store(data,length))r1_health_event_notification_throttle(6);
 else record_error("[RING]sleep data storage fail","sleep data storage fail");
}
/* Ordinary C for stock sector erase/count and erase event thunk. The count
 * is a byte-truncated partition size; snapshot it before erasing. Reload the
 * partition/device before every command, including after FAL callbacks. */
#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_sleep_sync_context_prefix[3];
__attribute__((section(".text.r1_sleep_sector_count"))) uint32_t r1_sleep_sector_count(void)
{
 volatile uint32_t *context=r1_sleep_sync_context_prefix;
 const volatile uint8_t *partition=(const volatile uint8_t *)(uintptr_t)context[1];
 return partition?(uint8_t)(read32(partition+56)>>12):0;
}
__attribute__((section(".text.r1_sleep_erase_all"))) void r1_sleep_erase_all(void)
{
 uint32_t count=r1_sleep_sector_count();
 volatile uint32_t *context=r1_sleep_sync_context_prefix;
 for(uint32_t sector=0;sector<count;sector++){
  const volatile uint8_t *partition=(const volatile uint8_t *)(uintptr_t)context[1];
  const volatile uint8_t *device=(const volatile uint8_t *)(uintptr_t)context[2];
  uint32_t offset=read32(partition+52)+(sector<<12);
  int (*erase)(long,size_t)=(void *)(uintptr_t)read32(device+48);
  (void)erase((long)offset,4096);
 }
}
__attribute__((section(".text.r1_event_service_0008dd88"))) void r1_event_service_0008dd88(void)
{r1_sleep_erase_all();}
/* Stock 0x5b32c: scan eight 24-byte headers per sector. The initialized
 * header persists across reads, including partial/failed FAL operations. */
extern void __aeabi_memclr(void *,size_t);
uint32_t r1_sleep_storage_valid_count(void)
{
 uint32_t sectors=r1_sleep_sector_count();
 uint32_t header[6];__aeabi_memclr(header,sizeof(header));
 uint32_t count=0;
 volatile uint32_t *context=r1_sleep_sync_context_prefix;
 for(uint32_t sector=0;sector<sectors;sector++){
  const volatile uint8_t *partition=(const volatile uint8_t *)(uintptr_t)context[1];
  uint32_t start=read32(partition+52)+(sector<<12)+16;
  for(uint32_t slot=0;slot<8;slot++){
   const volatile uint8_t *device=(const volatile uint8_t *)(uintptr_t)context[2];
   int (*read)(long,void *,size_t)=(void *)(uintptr_t)read32(device+40);
   (void)read((long)(start+slot*24),header,sizeof(header));
   if(header[2]==UINT32_MAX || header[3]==UINT32_MAX)break;
   count=(uint8_t)(count+1);
  }
 }
 return count;
}
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
void r1_sleep_storage_delete_all(void)
{
 uint32_t count=r1_sleep_storage_valid_count();
 if(count)r1_sleep_erase_all();
 const char *ring="[RING]sleep storage data delete all, sleep num: %d";
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000u,ring,ring,count);
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_1(0x001c0003u,"sleep storage data delete all, sleep num: %d",count);
}
