/* SPDX-License-Identifier: MIT
 * Native image-A XIP padmux 0x1020658c/0x102065b8/0x102065dc/
 * 0x10206630 and GPIO direction 0x10205f24. MMIO nibble layout and the
 * exact 32-pair default pin table come from authenticated stock bytes.
 */
#include <stdint.h>

static const uint8_t gx8002_xip_padmux_defaults_1020acc4[64] = {
    0,0, 1,0, 2,0, 3,0, 4,0, 5,0, 6,0, 7,0,
    8,0, 9,0, 10,0, 11,0, 12,0, 13,0, 14,0, 15,0,
    16,0, 17,0, 18,0, 19,0, 20,0, 21,0, 22,0, 23,0,
    24,0, 25,0, 26,0, 27,0, 28,0, 29,0, 30,0, 31,0
};

int32_t gx8002_xip_padmux_get_1020658c(uint32_t pin)
{
    if (pin >= 33u) return -1;
    volatile const uint32_t *const registers =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0xa0010090);
    return (int32_t)((registers[pin >> 3] >> ((pin & 7u) * 4u)) & 15u);
}

int32_t gx8002_xip_padmux_check_102065b8(uint32_t pin,
                                             uint32_t function)
{
    if ((int32_t)pin < 0 || (int32_t)function < 0) return -1;
    uint32_t current = (uint8_t)gx8002_xip_padmux_get_1020658c(pin);
    return current == function ? 0 : -1;
}

int32_t gx8002_xip_padmux_set_102065dc(uint32_t pin, uint32_t function)
{
    if (pin >= 33u) return -1;
    volatile uint32_t *const registers =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010090);
    uint32_t shift = (pin & 7u) * 4u;
    volatile uint32_t *word = &registers[pin >> 3];
    *word = (*word & ~(15u << shift)) | ((function & 15u) << shift);
    return gx8002_xip_padmux_check_102065b8(pin, function) == 0 ? 0 : -1;
}

int32_t gx8002_xip_padmux_initialize_10206630(const uint8_t *pairs,
                                                  int32_t pair_count)
{
    if (pairs == 0 || pair_count < 0) return -1;
    for (uint32_t pin = 0; pin < 32u; ++pin) {
        uint8_t default_pin = gx8002_xip_padmux_defaults_1020acc4[pin * 2u];
        uint8_t function = gx8002_xip_padmux_defaults_1020acc4[pin * 2u + 1u];
        for (int32_t index = 0; index < pair_count; ++index) {
            if (pairs[index * 2] == default_pin) {
                function = pairs[index * 2 + 1];
                break;
            }
        }
        (void)gx8002_xip_padmux_set_102065dc(default_pin, function);
    }
    return 0;
}

uint32_t gx8002_xip_gpio_set_direction_10205f24(uint32_t pin,
                                                   uint32_t direction)
{
    pin &= 31u;
    volatile uint32_t *const output_enable =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0001000);
    volatile uint32_t *const input_enable =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0001008);
    uint32_t bit = 1u << pin;
    if (direction == 1u) {
        *input_enable &= ~bit;
        *output_enable |= bit;
    } else if (direction == 0u) {
        *output_enable &= ~bit;
        *input_enable |= bit;
    } else if (direction == 2u) {
        *input_enable &= ~bit;
        *output_enable &= ~bit;
    }
    return 0u;
}
