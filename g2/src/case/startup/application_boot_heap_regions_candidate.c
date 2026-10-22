/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800bf54/0x0800bf6c RAM region descriptors.
 * These are two RAM addresses and a size from native literals, not copied RAM.
 * The second address is not assumed to be the end of the first region.
 */
#include <stdint.h>

/* Stock 0x0800BF54 (case_boot_heap_region_a) */
uint32_t case_boot_heap_region_a(uint32_t *first,uint32_t *second,uint32_t *bytes)
{
    *first=0x200015d0u;
    *second=0x2000162cu;
    *bytes=128u;
    return 128u;
}

/* Stock 0x0800BF6C (case_boot_heap_region_b) */
uint32_t case_boot_heap_region_b(uint32_t *first,uint32_t *second,uint32_t *bytes)
{
    *first=0x2000182cu;
    *second=0x20001888u;
    *bytes=256u;
    return 256u;
}
