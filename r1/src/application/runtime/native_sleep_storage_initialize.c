/* Stock sleep FAL binding 0x5b0f8 and service thunk 0x8dd8c.
 * Reuse the existing three-word sleep context; preserve partial failure state. */
#include <stdint.h>
#include <stddef.h>
#include <fal.h>
extern uint32_t r1_sleep_sync_context_prefix[3];
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
_Static_assert(sizeof(uintptr_t)==4 && offsetof(struct fal_partition,flash_name)==28,"native sleep FAL name offset");
#define TEXT(name,value) const char r1_sleep_bind_##name[] __attribute__((section(".r1.sleep.bind." #name),aligned(1)))=value
TEXT(partition,"sleep.db");
TEXT(partition_ring,"[RING]sleep db not find fal partition");
TEXT(partition_sdk,"sleep db not find fal partition");
TEXT(device_ring,"[RING]log flash not find fal flash device");
TEXT(device_sdk,"log flash not find fal flash device");
#undef TEXT
static void missing(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0001,sdk);
}
void r1_sleep_db_fal_bind(void)
{
    volatile uint32_t *context=r1_sleep_sync_context_prefix;
    const struct fal_partition *partition=fal_partition_find(r1_sleep_bind_partition);
    context[1]=(uint32_t)(uintptr_t)partition;
    if (partition==NULL) {
        missing(r1_sleep_bind_partition_ring,r1_sleep_bind_partition_sdk);
        return;
    }
    const struct fal_flash_dev *device=fal_flash_device_find(partition->flash_name);
    context[2]=(uint32_t)(uintptr_t)device;
    if (device!=NULL) {
        ((volatile uint8_t *)context)[0]=1;
        return;
    }
    missing(r1_sleep_bind_device_ring,r1_sleep_bind_device_sdk);
    context[1]=0;
}
void r1_native_sleep_database_initialize(void)
{
    r1_sleep_db_fal_bind();
}
