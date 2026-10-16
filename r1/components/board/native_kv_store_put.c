/* Recovered R1 erase-on-wrap and write policy; lower flash driver is external. */
#include <stdint.h>
#include <stddef.h>
extern void *volatile r1_kv_storage_context;
extern volatile uint8_t r1_kv_block_cursor,r1_kv_block_count,r1_kv_erase_threshold;
extern volatile uint32_t r1_kv_block_stride;
struct info_view { uint8_t reserved[52];volatile uint32_t block_base; };
struct driver_view { uint8_t reserved[44];uint32_t (*volatile write)(uint32_t,const void *,uint32_t);uint32_t (*volatile erase)(uint32_t,uint32_t); };
extern void *volatile r1_kv_storage_driver;
_Static_assert(offsetof(struct info_view,block_base)==52,"native base offset");
_Static_assert(offsetof(struct driver_view,write)==44,"native write offset");
_Static_assert(offsetof(struct driver_view,erase)==48,"native erase offset");
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
#define TEXT(n,s) const char r1_kv_put_##n[] __attribute__((section(".r1.kv.put.log." #n),aligned(1)))=s
TEXT(erase_ring,"[RING]Flash erase failed, offset: 0x%08X");
TEXT(erase_sdk,"Flash erase failed, offset: 0x%08X");
TEXT(reset_ring,"[RING]Erased entire sector, reset slot to 0");
TEXT(reset_sdk,"Erased entire sector, reset slot to 0");
TEXT(write_ring,"[RING]Flash write failed, slot: %d, offset: 0x%08X");
TEXT(write_sdk,"Flash write failed, slot: %d, offset: 0x%08X");
uint32_t r1_kv_store_put(uint32_t offset,const void *source,uint32_t bytes)
{
 if (!r1_kv_storage_context) return 6;
 if (!r1_kv_storage_driver) return 6;
 if (!source || !bytes) return 1;
 uint32_t cursor=r1_kv_block_cursor;
 if (cursor>=r1_kv_erase_threshold) {
  for (uint32_t slot=0;slot<r1_kv_block_count;slot++) {
   uint32_t address=((struct info_view *)r1_kv_storage_context)->block_base+(slot<<12);
   if (((struct driver_view *)r1_kv_storage_driver)->erase(address,4096)) {
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
     r1_structured_log_format(0x04400000,r1_kv_put_erase_ring,r1_kv_put_erase_ring,((struct info_view *)r1_kv_storage_context)->block_base);
    if (r1_structured_log_mode_get()&2u)
     nrf_log_frontend_std_1(0x001c0001,r1_kv_put_erase_sdk,((struct info_view *)r1_kv_storage_context)->block_base);
    return 1;
   }
  }
  r1_kv_block_cursor=0;
  if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   r1_structured_log_format(0x0c000000,r1_kv_put_reset_ring,r1_kv_put_reset_ring);
  if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0003,r1_kv_put_reset_sdk);
 }
 uint32_t base=((struct info_view *)r1_kv_storage_context)->block_base;
 uint32_t slot=r1_kv_block_cursor,stride=r1_kv_block_stride;
 uint32_t address=base+slot*stride+offset;
 if (!((struct driver_view *)r1_kv_storage_driver)->write(address,source,bytes)) return 0;
 if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x04800000,r1_kv_put_write_ring,r1_kv_put_write_ring,(uint32_t)r1_kv_block_cursor,address);
 if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_2(0x001c0001,r1_kv_put_write_sdk,r1_kv_block_cursor,address);
 return 1;
}
