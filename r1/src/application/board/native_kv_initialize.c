/* R1 KV initialization policy. FAL, CMSIS and native scans are providers. */
#include <stdint.h>
#include <stddef.h>
extern void *volatile r1_kv_mutex;
extern volatile uint8_t r1_kv_block_cursor;
void *volatile r1_kv_storage_context __attribute__((section(".r1.kv.storage_context")));
void *volatile r1_kv_storage_driver __attribute__((section(".r1.kv.storage_driver")));
volatile uint8_t r1_kv_block_count __attribute__((section(".r1.kv.block_count")));
volatile uint8_t r1_kv_erase_threshold __attribute__((section(".r1.kv.erase_threshold")));
volatile uint32_t r1_kv_block_stride __attribute__((section(".r1.kv.block_stride")));
volatile uint32_t r1_kv_partition_size __attribute__((section(".r1.kv.partition_size")));
static uint8_t mutex_storage[80] __attribute__((section(".r1.kv.mutex_storage"),aligned(4)));
#define TEXT(n,s) const char r1_kv_init_##n[] __attribute__((section(".r1.kv.init.log." #n),aligned(1)))=s
TEXT(mutex_name,"kv_mutex");TEXT(partition_name,"kv.bin");
TEXT(part_ring,"[RING]kv flash not find fal partition");TEXT(part_sdk,"kv flash not find fal partition");
TEXT(driver_ring,"[RING]kv flash not find fal flash device");TEXT(driver_sdk,"kv flash not find fal flash device");
TEXT(size_ring,"[RING]kv flash len is too small, len:%d, need:%d");TEXT(size_sdk,"kv flash len is too small, len:%d, need:%d");
TEXT(ready_ring,"[RING]kv user init, ofs:%d, len:%d, slot:%d, max_slot:%d");TEXT(ready_sdk,"kv user init, ofs:%d, len:%d, slot:%d, max_slot:%d");
struct mutex_attr { const char *name;uint32_t bits;void *memory;uint32_t size; };
const struct mutex_attr r1_kv_mutex_attributes __attribute__((section(".r1.kv.mutex_attributes")))={r1_kv_init_mutex_name,0,mutex_storage,80};
struct partition_view { uint8_t reserved[28];char device_name[24];volatile uint32_t offset,length; };
_Static_assert(offsetof(struct partition_view,offset)==52 && offsetof(struct partition_view,length)==56,"FAL partition layout");
extern void *osMutexNew(const void *);
extern uint32_t r1_fal_is_initialized(void);
extern int fal_init(void);
extern const void *fal_partition_find(const char *);
extern const void *fal_flash_device_find(const char *);
extern void r1_kv_flash_erase_scan(void);
extern uint32_t r1_latest_valid_flash_slot_scan_adapter(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_kv_port_initialize(void)
{
 if (!r1_kv_mutex) r1_kv_mutex=osMutexNew(&r1_kv_mutex_attributes);
 if (!r1_fal_is_initialized()) (void)fal_init();
 r1_kv_storage_context=(void *)fal_partition_find(r1_kv_init_partition_name);
 if (!r1_kv_storage_context) {
  if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) r1_structured_log_format(0x04000000,r1_kv_init_part_ring,r1_kv_init_part_ring);
  if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0001,r1_kv_init_part_sdk);
  return 6;
 }
 r1_kv_storage_driver=(void *)fal_flash_device_find((char *)r1_kv_storage_context+28);
 if (!r1_kv_storage_driver) {
  if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) r1_structured_log_format(0x04000000,r1_kv_init_driver_ring,r1_kv_init_driver_ring);
  if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0001,r1_kv_init_driver_sdk);
  r1_kv_storage_context=0;return 6;
 }
 uint32_t length=((struct partition_view *)r1_kv_storage_context)->length;
 if (length<2048) {
  if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) r1_structured_log_format(0x04800000,r1_kv_init_size_ring,r1_kv_init_size_ring,((struct partition_view *)r1_kv_storage_context)->length,2048u);
  if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_2(0x001c0001,r1_kv_init_size_sdk,((struct partition_view *)r1_kv_storage_context)->length,2048);
  return 1;
 }
 r1_kv_erase_threshold=(uint8_t)(length/2048);
 r1_kv_block_stride=2048;r1_kv_partition_size=length;
 r1_kv_block_count=(uint8_t)(length>>12);
 r1_kv_flash_erase_scan();r1_kv_block_cursor=(uint8_t)r1_latest_valid_flash_slot_scan_adapter();
 if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
  struct partition_view *p=r1_kv_storage_context;
  r1_structured_log_format(0x0d000000,r1_kv_init_ready_ring,r1_kv_init_ready_ring,p->offset,p->length,(uint32_t)r1_kv_block_cursor,(uint32_t)r1_kv_erase_threshold);
 }
 if (r1_structured_log_mode_get()&2u) {
  struct partition_view *p=r1_kv_storage_context;
  nrf_log_frontend_std_4(0x001c0003,r1_kv_init_ready_sdk,p->offset,p->length,r1_kv_block_cursor,r1_kv_erase_threshold);
 }
 return 0;
}
