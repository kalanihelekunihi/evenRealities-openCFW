/* SPDX-License-Identifier: MIT
 * Image-B 0x10008154/0x100081b8: SPI pin mode and output control.
 */
#include <stdint.h>

static volatile uint32_t *const spi_gpio =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0001000);

uint32_t gx8002_image_b_spi_pin_mode_10008154(
    uint32_t pin, uint32_t mode)
{
    pin &= 31u;
    uint32_t mask = UINT32_C(1) << pin;
    if (mode == 1u) {
        spi_gpio[0x08u / 4u] &= ~mask;
        spi_gpio[0] |= mask;
    } else if (mode == 0u) {
        spi_gpio[0] &= ~mask;
        spi_gpio[0x08u / 4u] |= mask;
    } else if (mode == 2u) {
        spi_gpio[0x08u / 4u] &= ~mask;
        spi_gpio[0] &= ~mask;
    }
    return 0u;
}

uint32_t gx8002_image_b_spi_pin_output_100081b8(
    uint32_t pin, uint32_t high)
{
    pin &= 31u;
    uint32_t mask = UINT32_C(1) << pin;
    uint32_t current = spi_gpio[0x04u / 4u];
    spi_gpio[0x04u / 4u] = high == 0u ? current & ~mask : current | mask;
    return 0u;
}
