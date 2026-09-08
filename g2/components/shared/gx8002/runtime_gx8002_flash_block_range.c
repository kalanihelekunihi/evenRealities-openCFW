/* SPDX-License-Identifier: MIT */
/* Recovered from package 0x158b8 and 0x15aa4. Output writes intentionally
 * precede device-state reads, including when callers alias state storage. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
int open_cfw_gx8002_flash_block_bounds(uint32_t address,
                                     volatile uint32_t *start,
                                     volatile uint32_t *end)
{
    *end=0;
    *start=0;
    if (open_cfw_gx8002_flash_state.device_index<0)
        return -1;
    uint32_t limit=open_cfw_gx8002_flash_state.usable_bytes & ~UINT32_C(4095);
    for (uint32_t base=0; base!=limit; base+=4096) {
        uint32_t next=base+4096;
        if (address>=base && address<next) {
            *start=base;
            *end=next;
            return 0;
        }
    }
    return -1;
}
int open_cfw_gx8002_flash_block_range(uint32_t address,uint32_t length,
                                    volatile uint32_t *start,
                                    volatile uint32_t *end)
{
    uint32_t temporary;
    int result=open_cfw_gx8002_flash_block_bounds(address,start,&temporary);
    if (result) return result;
    return open_cfw_gx8002_flash_block_bounds(address+length-1,&temporary,end);
}
extern int open_cfw_gx8002_flash_wait_ready(void);
int open_cfw_gx8002_flash_sync(void)
{
    return open_cfw_gx8002_flash_wait_ready();
}
