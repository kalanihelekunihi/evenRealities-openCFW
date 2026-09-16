/* SPDX-License-Identifier: MIT */
/* Backup package 0x3ff10. Preserve output/state alias order and observed r0.
 * Callers' interpretation of the return value remains to be established. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
int open_cfw_gx8002_flash_block_range(uint32_t address,uint32_t length,
                                    volatile uint32_t *start,
                                    volatile uint32_t *end)
{
    *start=0;
    if (open_cfw_gx8002_flash_state.device_index<0) return (int)address;
    uint32_t limit=open_cfw_gx8002_flash_state.usable_bytes&~4095u;
    for (uint32_t base=0;base!=limit;base+=4096u) {
        uint32_t next=base+4096u;
        if (address>=base && address<next) {
            *start=base;
            *end=0;
            if (open_cfw_gx8002_flash_state.device_index<0) return (int)address;
            limit=open_cfw_gx8002_flash_state.usable_bytes&~4095u;
            if (!limit) return (int)address;
            address+=length-1u;
            for (base=0;base!=limit;base+=4096u) {
                next=base+4096u;
                if (address>=base && address<next) {
                    *end=next;
                    break;
                }
            }
            return (int)address;
        }
    }
    return (int)address;
}
