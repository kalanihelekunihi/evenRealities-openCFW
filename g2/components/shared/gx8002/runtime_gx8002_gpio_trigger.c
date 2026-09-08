/* SPDX-License-Identifier: MIT */
/* Recovered trigger registration; unsupported trigger values still register. */
#include <stdint.h>
#include <stddef.h>
#include <driver/gx_gpio.h>
struct gpio_callback_record {
    unsigned int port;
    GPIO_CALLBACK callback;
    void *private_data;
};
_Static_assert(sizeof(struct gpio_callback_record) == 12, "GPIO record ABI");
extern volatile struct gpio_callback_record open_cfw_gx8002_gpio_callbacks[32];
extern int open_cfw_gx8002_gpio_set_direction(unsigned int, GX_GPIO_DIRECTION);
extern int open_cfw_gx8002_gpio_isr(int, void *);
extern void open_cfw_gx8002_request_irq(int, int (*)(int, void *), void *);
#define GPIO_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(0xa0001000u + (offset)))
int open_cfw_gx8002_gpio_enable_trigger(unsigned int port, GX_GPIO_TRIGGER_EDGE trigger,
                                      GPIO_CALLBACK callback, void *private_data)
{
    if (port >= 32) return -1;
    open_cfw_gx8002_gpio_set_direction(port, GX_GPIO_DIRECTION_INPUT);
    volatile struct gpio_callback_record *record = &open_cfw_gx8002_gpio_callbacks[port];
    record->port = port;
    record->callback = callback;
    record->private_data = private_data;
    uint32_t bit = UINT32_C(1) << port;
    switch (trigger) {
    case GX_GPIO_TRIGGER_EDGE_FALLING: GPIO_WORD(0x2c) |= bit; break;
    case GX_GPIO_TRIGGER_EDGE_RISING: GPIO_WORD(0x28) |= bit; break;
    case GX_GPIO_TRIGGER_EDGE_BOTH: GPIO_WORD(0x24) |= bit; break;
    case GX_GPIO_TRIGGER_LEVEL_HIGH: GPIO_WORD(0x14) |= bit; break;
    case GX_GPIO_TRIGGER_LEVEL_LOW: GPIO_WORD(0x18) |= bit; break;
    default: break;
    }
    open_cfw_gx8002_request_irq(1, open_cfw_gx8002_gpio_isr, NULL);
    return 0;
}
