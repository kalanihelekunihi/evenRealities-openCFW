/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10205ee0 ISR and 0x10206074 disable trigger.
 * Literal pools in stock Codec resolve callback table to 0x20027930.
 * GPIO pending/configuration registers are in the 0xa0001000 block.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_gpio_set_direction_10205f24(
    uint32_t pin, uint32_t direction);
extern void gx8002_resident_request_irq_2553c(
    uint32_t number, uint32_t handler, uint32_t context);

typedef void (*gpio_callback)(uint32_t pin, uint32_t context);

uint32_t gx8002_xip_gpio_isr_10205ee0(void)
{
    volatile uint32_t *const pending =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0001030);
    volatile uint32_t *const callbacks =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027930);
    uint32_t snapshot = *pending;
    for (uint32_t pin = 0u; pin < 32u; ++pin) {
        uint32_t bit = 1u << pin;
        uint32_t acknowledgment = *pending;
        uint32_t function = callbacks[pin * 3u + 1u];
        if ((snapshot & bit) != 0u && function != 0u) {
            acknowledgment = bit;
            ((gpio_callback)(uintptr_t)(function & ~1u))(
                callbacks[pin * 3u], callbacks[pin * 3u + 2u]);
        }
        *pending = acknowledgment;
    }
    return 0u;
}

uint32_t gx8002_xip_gpio_enable_trigger_10205fb4(
    uint32_t pin, uint32_t trigger, uint32_t callback, uint32_t context)
{
    if (pin >= 32u) return UINT32_MAX;
    (void)gx8002_xip_gpio_set_direction_10205f24(pin, 0u);
    volatile uint32_t *const entry =
        (volatile uint32_t *)(uintptr_t)(UINT32_C(0x20027930) + pin * 12u);
    entry[0] = pin;
    entry[1] = callback;
    entry[2] = context;

    /* Eight native table entries at 0x1020aca4 branch to five writes;
     * modes 5-7 branch directly to the IRQ registration epilogue. */
    static const uint8_t enable_offsets[8] = {
        0x2cu, 0x28u, 0x24u, 0x14u, 0u, 0u, 0u, 0x18u
    };
    uint32_t index = trigger - 1u;
    if (index < 8u && enable_offsets[index] != 0u) {
        volatile uint32_t *reg = (volatile uint32_t *)(uintptr_t)(
            UINT32_C(0xa0001000) + enable_offsets[index]);
        *reg = *reg | (1u << pin);
    }
    gx8002_resident_request_irq_2553c(
        1u, (uint32_t)(uintptr_t)&gx8002_xip_gpio_isr_10205ee0, 0u);
    return 0u;
}

uint32_t gx8002_xip_gpio_disable_trigger_10206074(uint32_t pin)
{
    if (pin >= 32u) return UINT32_MAX;
    (void)gx8002_xip_gpio_set_direction_10205f24(pin, 2u);
    const uint32_t keep = ~(1u << pin);
    static const uint8_t offsets[] = {0x14u, 0x18u, 0x28u, 0x2cu, 0x24u};
    volatile uint8_t *const gpio =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0xa0001000);
    for (uint32_t i = 0u; i < 5u; ++i) {
        volatile uint32_t *reg =
            (volatile uint32_t *)(void *)(gpio + offsets[i]);
        *reg = *reg & keep;
    }
    volatile uint32_t *const entry =
        (volatile uint32_t *)(uintptr_t)(UINT32_C(0x20027930) + pin * 12u);
    entry[0] = 0xffu;
    entry[1] = 0u;
    entry[2] = 0u;
    return 0u;
}
