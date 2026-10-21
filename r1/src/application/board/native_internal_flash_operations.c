/* Native lower flash adapters and completion policy over pinned Nordic APIs. */
#include <stdint.h>
#include <stddef.h>
#include <nrf_fstorage.h>
extern nrf_fstorage_t r1_internal_flash_context;
volatile uint8_t r1_internal_flash_pending __attribute__((section(".r1.flash.pending")));
extern void nrf_sdh_evts_poll(void);
extern uint32_t r1_native_watchdog_hw_feed(void);
extern int32_t osDelay(uint32_t);
void r1_internal_flash_wait(nrf_fstorage_t *context)
{
 while (nrf_fstorage_is_busy(context)) {
  nrf_sdh_evts_poll();(void)r1_native_watchdog_hw_feed();(void)osDelay(5);
 }
}
void r1_internal_flash_event_handler(nrf_fstorage_evt_t *event)
{
 if (event->result==0 && (uint8_t)event->id<=2) r1_internal_flash_pending=0;
}
uint32_t r1_internal_flash_page_erase(uint32_t offset,uint32_t bytes)
{
 uint32_t base=r1_internal_flash_context.start_addr+offset;
 uint32_t page=*(volatile uint32_t *)0x10000010;
 uint32_t count=bytes/page+(bytes%page!=0);
 for (uint32_t i=0;i<count;i++) {
  r1_internal_flash_pending=1;
  (void)nrf_fstorage_erase(&r1_internal_flash_context,base+i*page,1,0);
  r1_internal_flash_wait(&r1_internal_flash_context);
 }
 return 1;
}
void r1_internal_flash_mapped_read(void *destination,uint32_t bytes,uint32_t offset)
{
 const volatile uint8_t *source=(const volatile uint8_t *)(uintptr_t)(r1_internal_flash_context.start_addr+offset);
 uint8_t *output=destination;
 for (uint32_t i=0;i<bytes;i++) output[i]=source[i];
}
uint32_t r1_internal_flash_word_write(const void *source,uint32_t bytes,uint32_t offset)
{
 uint32_t words=(bytes>>2)+((bytes&3u)!=0);
 /* Native volatile FICR access is retained even though its value is discarded. */
 (void)*(volatile uint32_t *)0x10000010;
 uint32_t address=r1_internal_flash_context.start_addr+offset;
 r1_internal_flash_pending=1;
 if (nrf_fstorage_write(&r1_internal_flash_context,address,source,words<<2,0)) return 0;
 r1_internal_flash_wait(&r1_internal_flash_context);return 1;
}
