/* Apollo Main display interface enable 0x471cd6..0x471d57, including the
 * pin-group mapping leaf at 0x471b9c..0x471bc9. */
#include <stdint.h>

extern uint32_t audio_uart_pin_mux_enable(uint32_t, uint32_t);
extern uint32_t g2_gpio_critical_save(void);

uint32_t audio_uart_display_pin_group_471b9c(uint32_t pin)
{
    if (pin <= 5u) return 4u;
    if (pin <= 9u) return 0u;
    if (pin >= 19u && pin <= 24u) return 5u;
    if (pin >= 25u && pin <= 27u) return 2u;
    return 7u;
}

uint32_t audio_uart_display_layer_prepare(uint32_t channel)
{
    if (channel == 14u || channel == 15u) return 3u;
    volatile uint32_t *const channel_reg =
        (volatile uint32_t *)(uintptr_t)(0x40008200u + (channel << 5u));
    const uint32_t pin = (*channel_reg >> 8u) & 0x1ffu;
    if (pin < 28u)
        (void)audio_uart_pin_mux_enable(audio_uart_display_pin_group_471b9c(pin),
                                         (channel + 34u) & 0xffu);

    const uint32_t saved = g2_gpio_critical_save();
    volatile uint32_t *const gate = (volatile uint32_t *)(uintptr_t)0x40008010u;
    *gate |= 1u << channel;
    *channel_reg |= 2u;
    *channel_reg &= ~2u;
    *channel_reg |= 1u;
    __asm volatile("msr primask, %0" : : "r"(saved) : "memory");
    return 0u;
}
