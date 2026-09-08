/* SPDX-License-Identifier: MIT */
/* Candidate: snapshot pending pins, dispatch live callbacks, acknowledge. */
#include <stdint.h>
#include <stddef.h>
#include <driver/gx_gpio.h>
struct gpio_callback_record {
    unsigned int port;
    GPIO_CALLBACK callback;
    void *private_data;
};
_Static_assert(sizeof(struct gpio_callback_record) == 12, "GPIO record stride");
_Static_assert(offsetof(struct gpio_callback_record, callback) == 4, "GPIO callback ABI");
extern volatile struct gpio_callback_record open_cfw_gx8002_gpio_callbacks[32];
int open_cfw_gx8002_gpio_isr(int irq, void *data)
{
    (void)irq;
    (void)data;
    volatile uint32_t *pending_register = (volatile uint32_t *)(uintptr_t)0xa0001030;
    uint32_t pending = *pending_register;
    volatile struct gpio_callback_record *record = open_cfw_gx8002_gpio_callbacks;
    for (unsigned int pin = 0; pin < 32; ++pin, ++record) {
        uint32_t mask = UINT32_C(1) << pin;
        if (pending & mask) {
            GPIO_CALLBACK callback = record->callback;
            if (callback) {
                void *private_data = record->private_data;
                unsigned int port = record->port;
                callback(port, private_data);
            }
            *pending_register = mask;
        }
    }
    return 0;
}
