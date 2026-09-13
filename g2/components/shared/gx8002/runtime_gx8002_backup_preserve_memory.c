/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Reconstructed composition of backup0x3c8f8 and0x3c93c.
 * Preserve the observed reads, including registers whose value is discarded.
 * Register names and physical reset-cause interpretation remain unconfirmed. */
uint32_t open_cfw_gx8002_backup_preserve_memory(void)
{
    uint32_t flags = *(volatile uint32_t *)(uintptr_t)0xa0000034u;
    if ((flags & 15u) == 0) {
        (void)*(volatile uint32_t *)(uintptr_t)0xa001002cu;
        return 0;
    }
    uint32_t preserve = *(volatile uint32_t *)(uintptr_t)0xa0010058u & 1u;
    (void)*(volatile uint32_t *)(uintptr_t)0xa001005cu;
    return preserve;
}
