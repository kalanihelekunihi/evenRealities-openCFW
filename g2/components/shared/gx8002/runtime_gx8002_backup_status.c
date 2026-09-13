/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Backup0x3c8f8. Preserve priority when multiple status bits are set. */
uint32_t open_cfw_gx8002_backup_status(void)
{
    uint32_t flags = *(volatile uint32_t *)(uintptr_t)0xa0000034u;
    if (flags & 1u) return 2;
    if (flags & 4u) return 3;
    if (flags & 8u) return 5;
    if (flags & 2u) return 4;
    return *(volatile uint32_t *)(uintptr_t)0xa001002cu & 1u;
}
