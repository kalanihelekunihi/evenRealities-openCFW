/* Stock 0x6b724: fixed-size pKey persistence through the shared FAL owner.
 * Keep the observed base+4 erased-word check and ignored device statuses. */
#include "native_health_storage.h"
#include "../../include/r1_stock_checksums.h"
#include <stddef.h>
#include <string.h>
extern void *pvPortMalloc(uint32_t);
extern void vPortFree(void *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
typedef int (*read_fn)(long,uint8_t *,size_t);
typedef int (*write_fn)(long,const uint8_t *,size_t);
typedef int (*erase_fn)(long,size_t);
static uint32_t word(uint32_t address)
{ return *(const volatile uint32_t *)(uintptr_t)address; }
static void report(uint32_t marker,uint32_t id,const char *ring,
                   const char *sdk,uint32_t value,uint32_t has_value)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        if (has_value) (void)r1_structured_log_format(marker,ring,ring,value);
        else (void)r1_structured_log_format(marker,ring,ring);
    }
    if (r1_structured_log_mode_get()&2u) {
        if (has_value) nrf_log_frontend_std_1(id,sdk,value);
        else nrf_log_frontend_std_0(id,sdk);
    }
}
void r1_health_pkey_store_native(const void *key,uint32_t length)
{
    if (length!=64) {
        report(0x04400000,0x001c0001,"[RING]gomore pKey len is err:%d",
               "gomore pKey len is err:%d",length,1);
        return;
    }
    if (!r1_health_pkey_storage.initialized) r1_pkey_fal_bind();
    if (!key) {
        report(0x04000000,0x001c0001,"[RING]gomore store pKey is null",
               "gomore store pKey is null",0,0);return;
    }
    if (!r1_health_pkey_storage.partition || !r1_health_pkey_storage.device) {
        report(0x04000000,0x001c0001,"[RING]gomore store flash not init",
               "gomore store flash not init",0,0);return;
    }
    uint8_t *copy=pvPortMalloc(length);
    if (!copy) {
        report(0x04000000,0x001c0001,"[RING]gomore store malloc failed",
               "gomore store malloc failed",0,0);return;
    }
    memcpy(copy,key,length);
    uint32_t crc=0;
    r1_stock_crc32_update(copy,length,&crc);
    volatile uint32_t header[2]={length,0};
    uint32_t partition=r1_health_pkey_storage.partition;
    uint32_t device=r1_health_pkey_storage.device;
    uint32_t base=word(partition+52u);
    read_fn read=(read_fn)(uintptr_t)word(device+40u);
    (void)read((long)(base+4u),(uint8_t *)(uintptr_t)header,8);
    if (header[0]!=UINT32_MAX) {
        device=r1_health_pkey_storage.device;
        partition=r1_health_pkey_storage.partition;
        erase_fn erase=(erase_fn)(uintptr_t)word(device+48u);
        base=word(partition+52u);
        (void)erase((long)base,4096);
        report(0x0c000000,0x001c0003,"[RING]gomore store erase",
               "gomore store erase",0,0);
    }
    header[0]=length;header[1]=crc;
    device=r1_health_pkey_storage.device;
    partition=r1_health_pkey_storage.partition;
    write_fn write=(write_fn)(uintptr_t)word(device+44u);
    base=word(partition+52u);
    (void)write((long)base,(const uint8_t *)(uintptr_t)header,8);
    partition=r1_health_pkey_storage.partition;
    device=r1_health_pkey_storage.device;
    base=word(partition+52u);
    write=(write_fn)(uintptr_t)word(device+44u);
    (void)write((long)(base+8u),copy,64);
    vPortFree(copy);
    report(0x0c400000,0x001c0003,"[RING]gomore store pKey success:%d",
           "gomore store pKey success:%d",64,1);
}
extern __typeof__(r1_health_pkey_store_native) r1_event_service_0006b724
    __attribute__((alias("r1_health_pkey_store_native")));
