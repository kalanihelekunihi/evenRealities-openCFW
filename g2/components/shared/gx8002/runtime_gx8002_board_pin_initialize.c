/* SPDX-License-Identifier: MIT
 * Recovered board pin initialization at package 0xfe2c.
 */
#include <stdint.h>
#include <driver/gx_padmux.h>
#include <driver/gx_gpio.h>
extern int open_cfw_gx8002_padmux_init(const GX_PIN_CONFIG *, int);
extern int open_cfw_gx8002_padmux_check(int, int);
extern int open_cfw_gx8002_gpio_set_direction(unsigned int, GX_GPIO_DIRECTION);
extern int open_cfw_gx8002_printf(const char *, ...);
extern void open_cfw_gx8002_board_pin_setup(void);

void open_cfw_gx8002_board_pin_initialize(void)
{
    const volatile GX_PIN_CONFIG *table = (const volatile GX_PIN_CONFIG *)(uintptr_t)0x1020ad30u;
    (void)open_cfw_gx8002_padmux_init((const GX_PIN_CONFIG *)(uintptr_t)0x1020ad30u, 13);
    for (unsigned int i = 0; i != 13; ++i) {
        unsigned int pin = table[i].pin_id;
        unsigned int function = table[i].function;
        if (open_cfw_gx8002_padmux_check(pin, function))
            open_cfw_gx8002_printf((const char *)(uintptr_t)0x1020ad97u, pin);
        if (function == (pin == 2 ? 0u : 1u))
            (void)open_cfw_gx8002_gpio_set_direction(pin, GX_GPIO_DIRECTION_INPUT);
    }
    open_cfw_gx8002_board_pin_setup();
    *(volatile uint32_t *)(uintptr_t)0x20027b4cu = 1;
}
