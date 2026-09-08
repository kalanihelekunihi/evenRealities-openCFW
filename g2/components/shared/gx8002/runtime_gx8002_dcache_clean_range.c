/* SPDX-License-Identifier: MIT */
/* Recovered fixed cache-controller command writes. The caller's size is not
 * increased for the discarded low address bits; this preserves stock. */
#include <stdint.h>
void open_cfw_gx8002_dcache_clean_range(void *address,int32_t size)
{
    uint32_t command=((uint32_t)(uintptr_t)address & UINT32_C(0xfffffff0))|8u;
    volatile uint32_t *operation=(volatile uint32_t *)UINT32_C(0xe000f004);
    while (size>=128) {
        *operation=command;
        *operation=command+16u;
        *operation=command+32u;
        *operation=command+48u;
        *operation=command+64u;
        *operation=command+80u;
        *operation=command+96u;
        *operation=command+112u;
        command+=128u;
        size-=128;
    }
    while (size>0) {
        *operation=command;
        command+=16u;
        size-=16;
    }
}
