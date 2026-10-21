/* SPDX-License-Identifier: MIT
 * Image-B 0x10008288: registered SPI IRQ callback. The caller at 0x100086a4
 * passes SRAM context 0x200176a4 as callback data through IRQ registration.
 */
#include <stdint.h>

uint32_t gx8002_image_b_spi_master_irq_10008288(
    uint32_t irq, volatile const uint8_t *context)
{
    (void)irq;
    volatile const uint8_t *controller =
        (volatile const uint8_t *)(uintptr_t)
            *(volatile const uint32_t *)(const void *)(context + 4u);
    uint32_t status =
        *(volatile const uint32_t *)(const void *)(controller + 0x30u);
    if ((status & 2u) != 0u) {
        (void)*(volatile const uint32_t *)(uintptr_t)UINT32_C(0x38);
    }
    if ((status & 8u) != 0u) {
        (void)*(volatile const uint32_t *)(uintptr_t)UINT32_C(0x3c);
    }
    return 0u;
}
