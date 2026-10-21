/* SPDX-License-Identifier: MIT
 * Locked Apollo510 UART interrupt status read at 0x42372a.
 */
#include <stdint.h>

uint32_t opencfw_boot_uart_interrupt_status(uint32_t context,
                                            uint32_t *status,
                                            uint8_t enabled)
{
    /* Stock reads module before the null/magic guard. On the target, address
     * zero is vector memory; retain that access ordering. */
    const uint32_t module = *(volatile const uint32_t *)(uintptr_t)(context + 0x28u);
    if (context == 0u ||
        ((*(volatile const uint32_t *)(uintptr_t)context & UINT32_C(0x01ffffff))
         != UINT32_C(0x01ea9e06)))
        return 2u;
    const uintptr_t register_address = UINT32_C(0x40039000) + (module << 12) +
                                       (enabled == 0u ? 0x3cu : 0x40u);
    *status = *(volatile const uint32_t *)register_address;
    return 0u;
}
