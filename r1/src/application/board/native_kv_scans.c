/* Native R1 startup scrub and latest-slot selection. Driver remains external. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
extern void *volatile r1_kv_storage_context,*volatile r1_kv_storage_driver;
extern volatile uint8_t r1_kv_block_count,r1_kv_erase_threshold;
extern volatile uint32_t r1_kv_block_stride;
struct info_view { volatile uint32_t magic;uint8_t reserved[48];volatile uint32_t base; };
struct driver_view { uint8_t reserved[40];uint32_t (*volatile read)(uint32_t,void *,uint32_t);uint8_t reserved44[4];uint32_t (*volatile erase)(uint32_t,uint32_t); };
_Static_assert(offsetof(struct driver_view,erase)==48,"native erase slot");
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
#define TEXT(n,s) const char r1_kv_scan_##n[] __attribute__((section(".r1.kv.scan.log." #n),aligned(1)))=s
TEXT(scrub_ring,"[RING]kv flash erase, magic_word: %08X, sector: %d");
TEXT(scrub_sdk,"kv flash erase, magic_word: %08X, sector: %d");
TEXT(found_ring,"[RING]Found latest valid slot: %d, next write slot: %d");
TEXT(found_sdk,"Found latest valid slot: %d, next write slot: %d");
TEXT(empty_ring,"[RING]No valid data found, starting from slot 0");
TEXT(empty_sdk,"No valid data found, starting from slot 0");
void r1_kv_flash_erase_scan(void)
{
 uint32_t header[6];memset(header,0,sizeof(header));
 struct driver_view *driver=r1_kv_storage_driver;
 if (!driver || !driver->read) return;
 for (uint32_t page=0;page<r1_kv_block_count;page++) {
  uint32_t base=((struct info_view *)r1_kv_storage_context)->base;
  driver=r1_kv_storage_driver;
  (void)driver->read(base+(page<<12),header,24);
  struct info_view *info=r1_kv_storage_context;
  if (header[3]==info->magic || header[3]==UINT32_MAX) continue;
  base=info->base;driver=r1_kv_storage_driver;
  (void)driver->erase(base+(page<<12),4096);
  if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   r1_structured_log_format(0x0c800000,r1_kv_scan_scrub_ring,r1_kv_scan_scrub_ring,header[3],page);
  if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_2(0x001c0003,r1_kv_scan_scrub_sdk,header[3],page);
 }
}
uint32_t r1_latest_valid_flash_slot_scan_adapter(void)
{
 int32_t slot=(int32_t)r1_kv_erase_threshold-1;
 for (;slot>=0;slot--) {
  uint32_t base=((struct info_view *)r1_kv_storage_context)->base;
  uint32_t address=base+(uint32_t)slot*r1_kv_block_stride;
  uint32_t header[6];memset(header,0,sizeof(header));
  struct driver_view *driver=r1_kv_storage_driver;
  if (!driver || !driver->read) continue;
  if (driver->read(address,header,24)!=24) continue;
  if (header[3]!=((struct info_view *)r1_kv_storage_context)->magic) continue;
  uint32_t next=(uint8_t)(slot+1);
  if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   r1_structured_log_format(0x0c800000,r1_kv_scan_found_ring,r1_kv_scan_found_ring,(uint32_t)slot,next);
  if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_2(0x001c0003,r1_kv_scan_found_sdk,(uint32_t)slot,next);
  return next;
 }
 if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x0c000000,r1_kv_scan_empty_ring,r1_kv_scan_empty_ring);
 if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0003,r1_kv_scan_empty_sdk);
 return 0;
}
