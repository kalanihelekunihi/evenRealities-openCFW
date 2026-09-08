/* SPDX-License-Identifier: MIT */
/* Recovered disable ordering; no GPIO register or callback-table bulk reset. */
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
#define GPIO_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(0xa0001000u + (offset)))
int open_cfw_gx8002_gpio_disable_trigger(unsigned int port)
{
    if (port >= 32) return -1;
    open_cfw_gx8002_gpio_set_direction(port, GX_GPIO_DIRECTION_HIZ);
    uint32_t keep = ~(UINT32_C(1) << port);
    GPIO_WORD(0x14) &= keep;
    GPIO_WORD(0x18) &= keep;
    GPIO_WORD(0x28) &= keep;
    GPIO_WORD(0x2c) &= keep;
    GPIO_WORD(0x24) &= keep;
    volatile struct gpio_callback_record *record = &open_cfw_gx8002_gpio_callbacks[port];
    record->port = 255;
    record->callback = NULL;
    record->private_data = NULL;
    return 0;
}
