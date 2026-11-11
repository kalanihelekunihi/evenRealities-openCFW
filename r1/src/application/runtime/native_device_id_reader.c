#include <stdint.h>
#include <string.h>
#include "native_gomore_authorization.h"
#include "../board/native_battery_memory.h"
extern uint32_t r1_advertising_controller_address_get(void *);
extern int r1_native_snprintf(char *,uint32_t,const char *,...);
/* Authenticated cold identity cache. Native copies the byte length without a
 * destination-capacity guard. Build-only ownership is not runtime admission. */
const char r1_device_id_cold_cache[25] __attribute__((section(".r1.device.id.cache.text")))="5c000000b16e4ecbb4fb4a59";
const void *volatile r1_device_id_cache_pointer __attribute__((section(".r1.device.id.cache.pointer"),aligned(4)))=r1_device_id_cold_cache;
volatile uint8_t r1_device_id_cache_length __attribute__((section(".r1.device.id.cache.length")))=24;
const char r1_device_id_format[] __attribute__((section(".r1.device.id.format")))="%08x%08x%08x";
__attribute__((used,noinline)) static void device_id_read_kernel(volatile uint32_t *frame)
{
 void *destination=(void *)(uintptr_t)frame[0];
 if(r1_gomore_authorization_state.device_id_cached_valid){
  uint32_t length=r1_device_id_cache_length;
  const void *source=r1_device_id_cache_pointer;
  (void)memcpy(destination,source,length);return;
 }
 (void)r1_advertising_controller_address_get((void *)(uintptr_t)(frame+2));
 uint32_t address_word=read32((const volatile uint8_t *)frame+9);
 uint32_t first=*(const volatile uint32_t *)(uintptr_t)0x10000060;
 uint32_t second=*(const volatile uint32_t *)(uintptr_t)0x10000064;
 frame[0]=first;frame[1]=second;
 (void)r1_native_snprintf(destination,25,r1_device_id_format,address_word,first,second);
}
/* The stock entry passed its saved register area to the worker. Only the
 * destination word and six writable address bytes in that area are consumed
 * by the C call graph; source callers do not observe returned registers. */
__attribute__((noinline)) void r1_native_device_id_read_boundary(void *destination)
{
    volatile uint32_t frame[5]={0};
    frame[0]=(uint32_t)(uintptr_t)destination;
    device_id_read_kernel(frame);
}
