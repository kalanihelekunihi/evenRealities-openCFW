#include "native_ep_storage.h"
#include "native_status_ring.h"
#include <stddef.h>
extern volatile uint8_t r1_ep_active;
extern void *volatile r1_ep_mutex;
extern void *xQueueCreateMutex(uint8_t),*pvPortMalloc(size_t);
extern void vPortFree(void *);
extern const struct r1_log_partition *fal_partition_find(const char *);
extern const struct r1_log_flash *fal_flash_device_find(const char *);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static uint32_t ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
uint32_t r1_ep_storage_initialize(void)
{
    if (r1_ep_storage_initialized)return 1;
    struct r1_log_partition *partition=(struct r1_log_partition *)fal_partition_find("ep.bin");
    r1_ep_storage_partition=partition;
    if (!partition) {
        const char *ring="[RING][ep] partition '%s' not found";
        if (ring_enabled())(void)r1_structured_log_format(0x04400000,ring,ring,"ep.bin");
        if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0001,"[ep] partition '%s' not found",(uint32_t)(uintptr_t)"ep.bin");
        return 0;
    }
    r1_ep_storage_flash=(struct r1_log_flash *)fal_flash_device_find((const char *)partition+28);
    if (!r1_ep_storage_flash) {
        const char *ring="[RING][ep] flash device not found";
        if (ring_enabled())(void)r1_structured_log_format(0x04000000,ring,ring);
        if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,"[ep] flash device not found");
        r1_ep_storage_partition=0;return 0;
    }
    if (r1_ep_storage_partition->length<8192) {
        const char *ring="[RING][ep] partition too small: %d < %d";
        if (ring_enabled())(void)r1_structured_log_format(0x04800000,ring,ring,r1_ep_storage_partition->length,8192u);
        if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0001,"[ep] partition too small: %d < %d",r1_ep_storage_partition->length,8192);
        r1_ep_storage_partition=0;r1_ep_storage_flash=0;return 0;
    }
    r1_ep_storage_initialized=1;return 1;
}
static uint32_t read32(const uint8_t *p)
{return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
void r1_ep_scan_cursor(void)
{
    uint8_t *buffer=pvPortMalloc(4096);
    if (!buffer) {
        const char *ring="[RING][ep] scan malloc failed";
        if (ring_enabled())(void)r1_structured_log_format(0x04000000,ring,ring);
        if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,"[ep] scan malloc failed");
        r1_ep_flash_cursor=0;return;
    }
    uint32_t empty=0,first_empty=0,newest_index=0,newest_time=0;
    for (uint32_t sector=0;sector<2;sector++) {
        if (!r1_ep_record_read(sector<<12,buffer,4096))continue;
        for (uint32_t i=0;i<512;i++) {
            uint32_t index=(uint16_t)(i+(sector<<9));
            const uint8_t *record=buffer+(i<<3);
            if ((record[0]&15u)==10) {
                uint32_t timestamp=read32(record+4);
                if (timestamp && timestamp>=newest_time) {newest_time=timestamp;newest_index=index;}
            } else if (!empty) {empty=1;first_empty=index;}
        }
    }
    r1_ep_flash_cursor=(uint16_t)(empty ? first_empty:(newest_index+1u)&1023u);
    const char *ring="[RING][ep] scan done, write_idx=%d (empty=%d)";
    if (ring_enabled())(void)r1_structured_log_format(0x0c800000,ring,ring,(uint32_t)r1_ep_flash_cursor,empty);
    if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003,"[ep] scan done, write_idx=%d (empty=%d)",r1_ep_flash_cursor,empty);
    vPortFree(buffer);
}
/* Stock 0x5e0ec is the guard's ensure-initialized wrapper. The lower FAL
 * initializer at 0x5e228 is named r1_ep_storage_initialize above. */
void r1_ep_plan_initialization(void)
{
    if (!r1_ep_mutex)r1_ep_mutex=xQueueCreateMutex(1);
    if (!r1_ep_active && r1_ep_storage_initialize()) {
        r1_ep_scan_cursor();r1_ep_active=1;
    }
}
