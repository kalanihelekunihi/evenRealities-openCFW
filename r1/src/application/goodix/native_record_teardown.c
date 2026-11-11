#include <stdint.h>
#include "goodix_mem.h"
/* These records own their buffers; release does not clear their fields. */
uint32_t r1_goodix_native_release_nullable(void *allocation)
{
    if (allocation) goodix_mem_free(allocation);
    return 0;
}
uint32_t r1_goodix_native_record_destroy(void *record)
{
    if (record) {
        uintptr_t base=(uintptr_t)record;
        static const uint16_t cells[]={0x1c0,0x1dc,0x1f4};
        for (uint32_t i=0;i<sizeof(cells)/sizeof(cells[0]);i++) {
            uint32_t allocation=*(const volatile uint32_t *)(base+cells[i]);
            if (allocation) goodix_mem_free((void *)(uintptr_t)allocation);
        }
        goodix_mem_free(record);
    }
    return 0;
}
uint32_t r1_goodix_native_extended_record_destroy(void *record)
{
    uint32_t allocation=*(const volatile uint32_t *)((uintptr_t)record+0x260u);
    (void)r1_goodix_native_release_nullable((void *)(uintptr_t)allocation);
    return r1_goodix_native_record_destroy(record);
}
