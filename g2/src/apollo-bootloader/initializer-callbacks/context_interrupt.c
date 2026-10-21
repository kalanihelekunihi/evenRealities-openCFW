/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#define CONTEXT_MAGIC 0x01123456u
#define IRQ_BASE 0x40050000u

/* Reconstructed from the locked 0x42c63a instruction body. The platform
 * register access remains a volatile MMIO operation in the source body. */
uint32_t opencfw_boot_context_interrupt_enable(const uint32_t *handle,
                                               uint32_t mask)
{
    if (handle == 0 || (handle[0] & 0x01ffffffu) != CONTEXT_MAGIC)
        return 2u;
    if ((int32_t)(mask << 30) < 0)
        return 6u;

    volatile uint32_t *const enable = (volatile uint32_t *)
        (IRQ_BASE + handle[1] * 0x1000u + 0x200u);
    *enable |= mask;
    return 0u;
}
