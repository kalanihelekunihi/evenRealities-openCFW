/* SPDX-License-Identifier: MIT */
/* Recovered register ordering; target qualification remains separate. */
#include <stdint.h>
#include <driver/gx_gpio.h>
#define GPIO_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(0xa0001000u + (offset)))
int open_cfw_gx8002_gpio_set_direction(unsigned int port, GX_GPIO_DIRECTION direction)
{
    uint32_t bit = UINT32_C(1) << (port & 31u);
    if (direction == GX_GPIO_DIRECTION_OUTPUT) {
        GPIO_WORD(8) &= ~bit;
        GPIO_WORD(0) |= bit;
    } else if (direction == GX_GPIO_DIRECTION_INPUT) {
        GPIO_WORD(0) &= ~bit;
        GPIO_WORD(8) |= bit;
    } else if (direction == GX_GPIO_DIRECTION_HIZ) {
        GPIO_WORD(8) &= ~bit;
        GPIO_WORD(0) &= ~bit;
    }
    return 0;
}
int open_cfw_gx8002_gpio_set_level(unsigned int port, GX_GPIO_LEVEL level)
{
    uint32_t bit = UINT32_C(1) << (port & 31u);
    uint32_t previous = GPIO_WORD(4);
    GPIO_WORD(4) = level ? previous | bit : previous & ~bit;
    return 0;
}
