/* Native R1 latest-slot read policy; the lower driver is an explicit provider. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
extern void *volatile r1_kv_storage_context;
extern volatile uint8_t r1_kv_block_cursor;
extern volatile uint32_t r1_kv_block_stride;
struct r1_kv_storage_info_view { volatile uint32_t magic;uint8_t reserved4[48];volatile uint32_t block_base; };
struct r1_kv_storage_driver_view { uint8_t reserved0[40];uint32_t (*volatile read)(uint32_t,void *,uint32_t); };
extern void *volatile r1_kv_storage_driver;
_Static_assert(offsetof(struct r1_kv_storage_info_view,block_base)==52,"native slot base");
_Static_assert(offsetof(struct r1_kv_storage_driver_view,read)==40,"native driver read callback");
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
#define TEXT(name,value) const char r1_kv_get_##name[] __attribute__((section(".r1.kv.get.log." #name),aligned(1)))=value
TEXT(invalid_ring,"[RING]No valid KV data found in any slot");
TEXT(invalid_sdk,"No valid KV data found in any slot");
TEXT(read_ring,"[RING]Flash read failed, slot: %d, offset: 0x%08X, read_offset: %d");
TEXT(read_sdk,"Flash read failed, slot: %d, offset: 0x%08X, read_offset: %d");
uint32_t r1_kv_store_get(uint32_t offset,void *destination,uint32_t bytes)
{
    struct r1_kv_storage_info_view *initial=r1_kv_storage_context;
    if (!initial) return 6;
    struct r1_kv_storage_driver_view *driver=r1_kv_storage_driver;
    if (!driver) return 6;
    if (!destination || !bytes) return 1;
    uint32_t count=r1_kv_block_cursor;
    if (!count) return 6;
    uint32_t slot=count-1u;
    uint32_t base=initial->block_base+slot*r1_kv_block_stride;
    uint32_t header[6];memset(header,0,sizeof(header));
    uint32_t returned=driver->read(base,header,sizeof(header));
    if (returned!=sizeof(header) || header[3]!=((struct r1_kv_storage_info_view *)r1_kv_storage_context)->magic) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x08000000,r1_kv_get_invalid_ring,r1_kv_get_invalid_ring);
        if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0002,r1_kv_get_invalid_sdk);
        return 6;
    }
    returned=((struct r1_kv_storage_driver_view *)r1_kv_storage_driver)->read(base+offset,destination,bytes);
    if (returned==bytes) return 0;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04c00000,r1_kv_get_read_ring,r1_kv_get_read_ring,slot,base,offset);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_3(0x001c0001,r1_kv_get_read_sdk,slot,base,offset);
    return 1;
}
