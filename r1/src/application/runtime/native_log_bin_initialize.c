#include "native_log_bin.h"
extern const struct r1_log_partition *fal_partition_find(const char *);
extern const struct r1_log_flash *fal_flash_device_find(const char *);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t),nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
static void error(const char *ring,const char *plain)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,plain);
}
void r1_log_bin_initialize(void)
{
    struct r1_log_partition *partition=(struct r1_log_partition *)fal_partition_find("log.bin");
    r1_log_bin_partition=partition;
    if (!partition) {error("[RING]log flash not find fal partition","log flash not find fal partition");return;}
    r1_log_bin_flash=(struct r1_log_flash *)fal_flash_device_find((const char *)partition+28);
    if (!r1_log_bin_flash) {
        error("[RING]log flash not find fal flash device","log flash not find fal flash device");
        r1_log_bin_partition=0;return;
    }
    r1_log_bin_sector=0;r1_log_bin_offset=0;
    uint32_t count=r1_log_bin_sector_count(),marker=0;
    for (uint32_t sector=0;sector<count;sector=(uint8_t)(sector+1)) {
        uint32_t address=r1_log_bin_partition->base+4+(sector<<12);
        (void)r1_log_bin_flash->read(address,&marker,4);
        nrf_log_frontend_std_3(0x001c0003,"log flash init sector: %d, head: %08X, offset: %08X",sector,marker,address);
        if (marker==UINT32_MAX) {
            r1_log_bin_sector=(uint8_t)sector;r1_log_bin_offset=0;break;
        }
    }
    nrf_log_frontend_std_2(0x001c0003,"log flash init sector: %d, offset: %d",r1_log_bin_sector,r1_log_bin_offset);
    r1_log_bin_initialized=1;
}
