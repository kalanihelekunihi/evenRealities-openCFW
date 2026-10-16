#include <stdint.h>
#include <string.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_advertising_controller_address_get(void *);
extern int r1_native_snprintf(char *,uint32_t,const char *,...);
/* Authenticated cold identity cache. Native copies the byte length without a
 * destination-capacity guard. Build-only ownership is not runtime admission. */
const char r1_device_id_cold_cache[25] __attribute__((section(".r1.device.id.cache.text")))="5c000000b16e4ecbb4fb4a59";
volatile uint8_t r1_device_id_cache_valid __attribute__((section(".r1.device.id.cache.valid")))=0;
const void *volatile r1_device_id_cache_pointer __attribute__((section(".r1.device.id.cache.pointer"),aligned(4)))=r1_device_id_cold_cache;
volatile uint8_t r1_device_id_cache_length __attribute__((section(".r1.device.id.cache.length")))=24;
const char r1_device_id_format[] __attribute__((section(".r1.device.id.format")))="%08x%08x%08x";
__attribute__((used,noinline)) static void device_id_read_kernel(volatile uint32_t *frame)
{
 void *destination=(void *)(uintptr_t)frame[0];
 if(r1_device_id_cache_valid){
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
/* Native push{r0,r1,r2,r3,r4,lr}: both cached copies and SVC address writes can
 * modify these saved words. Restore their actual contents, not original args. */
__attribute__((naked,noinline)) void r1_native_device_id_read_boundary(void *destination __attribute__((unused)))
{__asm__ volatile("push {r0,r1,r2,r3,r4,lr}\nmov r0,sp\nbl device_id_read_kernel\npop {r0,r1,r2,r3,r4,pc}");}
