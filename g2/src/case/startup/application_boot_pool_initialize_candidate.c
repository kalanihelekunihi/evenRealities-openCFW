/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ae74 fixed-slot pool initialization.
 */
#include <stdint.h>
extern void case_boot_pool_prepare(uint32_t region,uint32_t mode); /* 0xc616 */
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
void case_boot_pool_initialize(uint32_t count,uint32_t stride,uint32_t storage,
                               uint32_t flags,uint32_t region)
{
    wr(region,storage);
    wr(region+0x3cu,count);
    wr(region+0x40u,stride);
    case_boot_pool_prepare(region,1u);
    *(volatile uint8_t *)(uintptr_t)(region+0x4cu)=(uint8_t)flags;
}
