#include "native_log_bin.h"
#include <stddef.h>
_Static_assert(offsetof(struct r1_log_partition,base)==52,"partition base");
_Static_assert(offsetof(struct r1_log_flash,read)==40,"flash read callback");
volatile uint8_t r1_log_bin_initialized __attribute__((section(".r1.log.bin.initialized")))=0;
volatile uint8_t r1_log_bin_sector __attribute__((section(".r1.log.bin.sector")))=0;
struct r1_log_partition *volatile r1_log_bin_partition __attribute__((section(".r1.log.bin.partition"),aligned(4)))=0;
struct r1_log_flash *volatile r1_log_bin_flash __attribute__((section(".r1.log.bin.flash"),aligned(4)))=0;
volatile uint32_t r1_log_bin_offset __attribute__((section(".r1.log.bin.offset"),aligned(4)))=0;
extern void r1_log_bin_initialize(void);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static void error(const char *ring,const char *plain)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,plain);
}
uint32_t r1_log_bin_sector_count(void)
{
    struct r1_log_partition *partition=r1_log_bin_partition;
    return partition ? (uint8_t)(partition->length>>12):0;
}
/* ARM UDIV produces zero for a zero divisor in the observed stock setup. */
static uint32_t next_sector(uint32_t sector,uint32_t count)
{uint32_t n=sector+1;return (uint8_t)(count ? n%count:n);}
void r1_log_bin_write(const void *data,uint32_t bytes)
{
    if (!r1_log_bin_initialized)r1_log_bin_initialize();
    if (!r1_log_bin_partition || !r1_log_bin_flash) {
        error("[RING]log flash not init","log flash not init");return;
    }
    if (!data || !bytes) {error("[RING]log data is null","log data is null");return;}
    if (bytes>4096) {
        const char *ring="[RING]log data too large, max size: %d";
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x04400000,ring,ring,4096u);
        if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0001,"log data too large, max size: %d",4096);
        return;
    }
    uint32_t count=r1_log_bin_sector_count();
    if (r1_log_bin_offset+bytes>4096) {
        uint32_t sector=next_sector(r1_log_bin_sector,count);
        r1_log_bin_sector=(uint8_t)sector;r1_log_bin_offset=0;
        struct r1_log_partition *partition=r1_log_bin_partition;
        uint32_t base=partition->base,address=base+(sector<<12);
        if (base+partition->length<address+4096u) {error("[RING]erase offset out of range","erase offset out of range");return;}
        uint32_t marker=0;
        (void)r1_log_bin_flash->read(address+4,&marker,4);
        if (marker!=UINT32_MAX) {
            nrf_log_frontend_std_2(0x001c0003,"erase offset: %08X, len: %d",address,4096);
            (void)r1_log_bin_flash->erase(address,4096);
        }
    }
    struct r1_log_partition *partition=r1_log_bin_partition;
    uint32_t base=partition->base;
    uint32_t address=base+r1_log_bin_offset+((uint32_t)r1_log_bin_sector<<12);
    if (base+partition->length<address+bytes) {error("[RING]write offset out of range","write offset out of range");return;}
    nrf_log_frontend_std_2(0x001c0003,"write offset: %08X, len: %d",address,bytes);
    (void)r1_log_bin_flash->write(address,data,bytes);
    r1_log_bin_offset=r1_log_bin_offset+bytes;
    uint32_t next=next_sector(r1_log_bin_sector,count);
    address=r1_log_bin_partition->base+(next<<12);
    uint32_t marker=0;
    (void)r1_log_bin_flash->read(address+4,&marker,4);
    if (marker==UINT32_MAX)return;
    partition=r1_log_bin_partition;
    if (partition->base+partition->length<address+4096u) {error("[RING]next sector erase offset out of range","next sector erase offset out of range");return;}
    nrf_log_frontend_std_2(0x001c0003,"next sector erase offset: %08X, len: %d",address,4096);
    (void)r1_log_bin_flash->erase(address,4096);
}
