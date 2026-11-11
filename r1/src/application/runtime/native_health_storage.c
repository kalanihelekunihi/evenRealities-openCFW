/* Stock 0x6ba68, 0x6ad80 and 0x6afb0: FAL-backed health-state recovery. */
#include "native_health_storage.h"
#include "../../include/r1_stock_checksums.h"
#include <stddef.h>
_Static_assert(sizeof(uintptr_t)==4 && sizeof(long)==4 && sizeof(size_t)==4,"R1 FAL ABI");
_Static_assert(sizeof(struct r1_health_pkey_storage)==12 && offsetof(struct r1_health_pkey_storage,partition)==4 && offsetof(struct r1_health_pkey_storage,device)==8,"native storage owner");
volatile struct r1_health_pkey_storage r1_health_pkey_storage
    __attribute__((section(".r1.health.pkey.storage"),aligned(4)))={0};
struct fal_partition;struct fal_flash_dev;
extern const struct fal_partition *fal_partition_find(const char *);
extern const struct fal_flash_dev *fal_flash_device_find(const char *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
typedef int (*flash_read_fn)(long,uint8_t *,size_t);
static uint32_t word(uint32_t at) { return *(const volatile uint32_t *)(uintptr_t)at; }
static flash_read_fn read_operation(uint32_t device) {
    return (flash_read_fn)(uintptr_t)word(device+40u);
}
static void note(const char *structured,const char *plain) {
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04000000u,structured,structured);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x1c0001u,plain);
}
void r1_pkey_fal_bind(void) {
    uint32_t partition=(uint32_t)(uintptr_t)fal_partition_find("pKey.bin");
    r1_health_pkey_storage.partition=partition;
    if (!partition) {
        note("[RING]log flash not find fal partition","log flash not find fal partition");
        return;
    }
    uint32_t device=(uint32_t)(uintptr_t)fal_flash_device_find((const char *)(uintptr_t)(partition+28u));
    r1_health_pkey_storage.device=device;
    if (!device) {
        note("[RING]log flash not find fal flash device","log flash not find fal flash device");
        r1_health_pkey_storage.partition=0;
        return;
    }
    r1_health_pkey_storage.initialized=1;
}
static uint64_t result(uint32_t low,uint32_t high) { return low | ((uint64_t)high<<32); }
uint64_t r1_health_pkey_load_native(void *key,uint32_t length,uint32_t seed0,uint32_t seed1) {
    volatile uint32_t header[2]={seed0,seed1};
    if (!r1_health_pkey_storage.initialized) r1_pkey_fal_bind();
    uint32_t partition=r1_health_pkey_storage.partition;
    if (!partition) goto unbound;
    uint32_t device=r1_health_pkey_storage.device;
    if (!device) goto unbound;
    if (!key || !length) {
        note("[RING]gomore store pKey is null","gomore store pKey is null");
        return result(0,length);
    }
    (void)read_operation(device)((long)word(partition+52u),(uint8_t *)(uintptr_t)header,8);
    if (header[0]!=64) {
        note("[RING]gomore store pKey not found","gomore store pKey not found");
        return result(0,length);
    }
    partition=r1_health_pkey_storage.partition;
    device=r1_health_pkey_storage.device;
    (void)read_operation(device)((long)(word(partition+52u)+8u),key,length);
    uint32_t computed=0;
    r1_stock_crc32_update(key,length,&computed);
    if (header[1]==computed) return result(1,computed);
    note("[RING]gomore store pKey crc32 not match","gomore store pKey crc32 not match");
    return result(0,computed);
unbound:
    note("[RING]gomore store flash not init","gomore store flash not init");
    return result(0,length);
}
uint64_t r1_health_lifecycle_restore_native(void *key,uint32_t key_length,void *state,uint32_t state_length) {
    volatile uint32_t header[2]={(uint32_t)(uintptr_t)state,state_length};
    uint32_t carry=key_length;
    if (!(uint32_t)r1_health_pkey_load_native(key,key_length,(uint32_t)(uintptr_t)state,state_length)) return result(0,carry);
    uint32_t aligned_state=(state_length+3u)&~3u;
    uint32_t aligned_key=(key_length+3u)&~3u;
    for (int32_t slot=3;slot>=0;--slot) {
        uint32_t partition=r1_health_pkey_storage.partition;
        uint32_t device=r1_health_pkey_storage.device;
        uint32_t offset=word(partition+52u)+aligned_key+8u+(aligned_state+8u)*(uint32_t)slot;
        (void)read_operation(device)((long)offset,(uint8_t *)(uintptr_t)header,8);
        uint32_t stored=header[0];
        if (stored==UINT32_MAX || stored!=state_length) continue;
        device=r1_health_pkey_storage.device;
        (void)read_operation(device)((long)(offset+8u),state,state_length);
        static const char message[]="[RING]gomore restore previousData len:%d,offset:%d";
        if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
            carry=offset;
            (void)r1_structured_log_format(0x0c800000u,message,message,aligned_state,offset);
        }
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_2(0x1c0003u,"gomore restore previousData len:%d,offset:%d",aligned_state,offset);
        return result(1,carry);
    }
    return result(0,carry);
}
