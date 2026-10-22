/* SPDX-License-Identifier: MIT
 * Image-A SRAM IRQ and protection-map setup for flash_interface_initialize.
 * Native entries: 0x10023ac0, 0x100246c4, 0x100254ac, 0x1002553c.
 */
#include <stdint.h>
#include "resident_product_data.h"


/* Stock 0x10023AC0 (flash_spi_irq_handler) */
uint32_t gx8002_resident_flash_spi_irq_handler_23ac0(void)
{
    const volatile uint32_t *const spi =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    uint32_t flags = spi[0x30u / 4u];
    if ((flags & 2u) != 0u) (void)spi[0x38u / 4u];
    if ((flags & 8u) != 0u) (void)spi[0x3cu / 4u];
    return 0u;
}

/* Stock 0x100246C4 (gx8002_flash_protection_initialize) */
void gx8002_resident_flash_protection_initialize_246c4(void)
{
    volatile uint32_t *const maps = gx8002_flash_protection_maps_26ff8;
    maps[0] = (uint32_t)(uintptr_t)gx8002_otp_protect_2657c;
    maps[1] = 5u;
    maps[2] = (uint32_t)(uintptr_t)gx8002_otp_protect_265a4;
    maps[3] = 7u;
    maps[4] = (uint32_t)(uintptr_t)gx8002_otp_protect_265dc;
    maps[5] = 9u;
}

/* Stock 0x100254AC (csi_vic_enable_irq) */
void gx8002_resident_vic_enable_irq_254ac(uint32_t number)
{
    volatile uint32_t *const enables =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100);
    enables[(number >> 5) & 3u] = UINT32_C(1) << (number & 31u);
}

/* Stock 0x1002553C (gx8002_request_irq) */
void gx8002_resident_request_irq_2553c(
    uint32_t number, uint32_t raw_handler_entry, uint32_t context)
{
    if (number >= 32u || raw_handler_entry == 0u) return;
    volatile uint32_t *const slots =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20026ef4);
    slots[number * 2u] = raw_handler_entry;
    slots[number * 2u + 1u] = context;
    gx8002_resident_vic_enable_irq_254ac(number);
}
